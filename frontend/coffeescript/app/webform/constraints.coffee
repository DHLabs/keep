define [], ->

  DOT_SHORTHAND = ///
    # Match any "."  surrounded by whitespace,
    (\s+\.\s+)
    # or the a "." at the start of an expression.
    | (^\.\s+)
  ///g

  # Regex for splitting an expression into tokens.
  SEPARATOR_REGEX = ///
    \s*(\(|\))\s*                # Parenthesis
    | \s*(\+|\-\s+|\*|div)\s*    # +,-,*,div
    | \s*(and|or|not)\s*         # and, or, not
    | \s*((\=\!)|\=)\s*          # =, !=
    | \s*(\<\=|\>\=|\>|\<)\s*    # >, <, <=, >=
  ///

  # Regex for checking if a token is an operand/value
  OPERAND_REGEX = ///
    ^YES|^NO                 # YES/NO
    | ^\$\{.*\}              # Selector
    | ^\".*\"|^\'.*\'        # String
    | ^[+-]?\d+(\.\d+)?$     # Number
  ///

  IS_BOOLEAN = /^YES|^NO/
  IS_SELECTOR = /^\$\{.*\}/
  IS_STRING = /^\".*\"|^\'.*\'/

  LEFT_PAREN  = '('
  RIGHT_PAREN = ')'

  OPS = [ '+', '-', '*', 'div', '=', '!=', '>', '<', '>=', '<=', 'and', 'or', 'not' ]

  PRECEDENCE =
    '*'   : 5
    'div' : 5
    '+'   : 4
    '-'   : 4
    '='   : 3
    '!='  : 3
    '>'   : 3
    '<'   : 3
    '>='  : 3
    '<='  : 3
    'not' : 2
    'and' : 1
    'or'  : 1

  COMPARE =
    '='   : (a, b) -> a is b
    '!='  : (a, b) -> a isnt b
    'and' : (a, b) -> a and b
    'or'  : (a, b) -> a or b
    '>'   : (a, b) -> a > b
    '<'   : (a, b) -> a < b
    '>='  : (a, b) -> a >= b
    '<='  : (a, b) -> a <= b
    'not' : (__, b) -> not b  # unary operator

  MATH =
    '+'   : (x, y) -> x + y
    '-'   : (x, y) -> x - y
    '*'   : (x, y) -> x * y
    'div' : (x, y) -> x / y



  # Helper methods for working with expressions
  top = -> this[this.length - 1]

  is_operand = (token) -> OPERAND_REGEX.test token
  is_operator = (token) -> OPS.indexOf(token) isnt -1

  precedence = (operator) -> PRECEDENCE[operator]

  parse_boolean = (val) -> if val is 'YES' then true else false

  is_number = (value) ->
    if /^(\-|\+)?([0-9]+(\.[0-9]+)?|Infinity)$/.test(value) \
    then true else false

  # Logical comparison
  compare = (value1, value2, operator) ->
    switch operator
      when '>', '<', '>=', '<='
        # Convert values to numbers before comparing
        return false unless is_number(value1)
        return false unless is_number(value2)
        value1 = Number.parseFloat value1
        value2 = Number.parseFloat value2
        COMPARE[operator] value1, value2
      when 'and', 'or'
        value1 = parse_boolean value1.toUpperCase() if value1 instanceof String
        value2 = parse_boolean value2.toUpperCase() if value1 instanceof String
        COMPARE[operator] value1, value2
      else # !=, =
        COMPARE[operator] value1, value2


  # Mathematical computation
  compute = (value1, value2, operator) -> MATH[operator] value1, value2


  class XFormConstraintChecker

    @passesConstraint: ( field, answers ) ->
      return true if not field.bind?.constraint?
      expression = field.bind.constraint
      expression = @replace_dot_shorthand(expression, field.name)
      expression = @evaluateSelectedInExpression(expression, answers, field.name)
      @evaluate_expression(expression, answers, field.name)


    @isRelevant: (field, answers) ->
      return true if not field.bind?.relevant?
      expression = field.bind.relevant
      expression = @replace_dot_shorthand(expression, field.name)
      expression = @evaluateSelectedInExpression(expression, answers, field.name)
      @evaluate_expression(expression, answers, field.name)


    # Replaces instances of the "." shorthand with the current field.
    # e.g. ". >= 0 and . =< 100" => "${grade} >= 0 and ${grade} =< 100"
    @replace_dot_shorthand: (expr, field) -> expr.replace DOT_SHORTHAND, " ${#{field}} "

    # Function replaces all "selected(.,'foo')" with evaluated boolean of YES or NO
    @evaluateSelectedInExpression: (expr, answers, currentPath) ->
      expression = expr

      loop
        # Exit if there are no more "selected(" strings present.
        start_range = expression.indexOf 'selected('
        end_range = expression.indexOf ')', start_range
        break if start_range is -1

        # Get the inner contents of the first "selected(...)"
        selected = expression[(start_range+'selected('.length) .. (end_range) ]

        # Get left, right parts of the string formatted as:
        # ${foo}, "bar"
        # Make the field name a selector if it's '.'
        [ field_name, expected_value ] = selected.split ','
        field_name = "${#{currentPath}}" if field_name is '.'

        # Remove ${} from field name, and quotes from expected value and
        # trim whitespace.
        field_name = field_name.replace /\s+/g, ""
        field_name = field_name[2 .. field_name.length - 2]
        expected_value = expected_value.replace /\s+/g, ""
        expected_value = expected_value[1 .. expected_value.length - 2]

        # Replace the "selected(...)" expression with YES or NO.
        response = answers[field_name]
        selected = expression[start_range .. end_range]
        result = if response is expected_value then 'YES' else 'NO'
        expression = expression.replace selected, result

      return expression


    @evaluate_expression: (expression, responses, current_field) ->
      tokens = @_tokenize(expression)
      @_process tokens, responses, current_field

    # Convert the expression into an array of tokens
    @_tokenize: (expression) ->
      # Split the string using our separator regex
      tokens = expression.split(SEPARATOR_REGEX)

      # Split includes 'undefined' for non-matching groups, we don't want that.
      # Remove trailing/leading whitespace and return the tokens.
      ( t.replace /^\s+|\s+$/g, '' for t in tokens when t? )

    # Parse the tokens using the Shunting-yard algorithm:
    # https://en.wikipedia.org/wiki/Shunting-yard_algorithm
    @_process: (tokens, responses, current_field) ->

      operator_stack = []
      operand_stack  = []
      operator_stack.top = top

      # If the operand is a selector, get the value.
      process_operand = (token) ->
        val = token

        if IS_SELECTOR.test token
          # Slice 'foo' from '${foo}'
          field_name = token.slice(2, token.length - 1)
          val = responses[field_name]

        if IS_BOOLEAN.test val
          parse_boolean(val)
        else if is_number(val)
          Number.parseFloat(val)
        else if IS_STRING.test val
          val.slice(1, val.length - 1) # Remove quotes
        else
          val

      # In the following, “process” means, (i) pop operand stack once (value1) (ii)
      # pop operator stack once (operator) (iii) pop operand stack again (value2)
      # (iv) compute value1 operator  value2 (v) push the value obtained in operand
      # stack.
      process = ->
        value2 = operand_stack.pop()
        value1 = operand_stack.pop()
        operator = operator_stack.pop()

        # Special case for unary "not" operator; put second value back on operand
        # stack.
        if operator is 'not'
          operand_stack.push value1 if value1

        result = switch operator
          when '+', '-', '*', 'div'
            value1 = Number.parseFloat value1
            value2 = Number.parseFloat value2
            compute(value1, value2, operator)
          else compare(value1, value2, operator)

        operand_stack.push result


      # Shunting-yard Algorithm:
      #
      # Until all tokens are processed, get one token and perform only one of
      # the steps.
      debugger
      for token in tokens

        # If the token is an operand, push it onto the operand stack.
        if is_operand(token) then operand_stack.push process_operand(token)

        # If the token is an operator, T1,
        else if is_operator(token)

          # while there is an operator token, T2, at the top of the operator
          # stack and the precedence of T1 is less than or equal to that of T,
          # process.
          while operator_stack.length > 0 \
            and precedence(token) <= precedence(operator_stack.top()) \
            then process()

          # at the end of the iteration push T1 onto the operator stack.
          operator_stack.push token

        # If the token is "(", then push it onto operator stack.
        else if token is LEFT_PAREN then operator_stack.push token

        # If the token is ")", then "process" as explained above until the
        # corresponding "(" is encountered in operator stack. At this stage POP
        # the operator stack and ignore "(."
        else if token is RIGHT_PAREN
          process() until operator_stack.top() is '('
          operator_stack.pop()

      # When there are no more input characters, keep processing until the
      # operator stack becomes empty.  The values left in the operand stack is
      # the final result of the expression.
      process() until operator_stack.length is 0
      operand_stack.pop()
