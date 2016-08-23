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
    | \s*(and|or|not|if)\s*      # and, or, not, if
    | \s*((\=\!)|\=)\s*          # =, !=
    | \s*(\<\=|\>\=|\>|\<)\s*    # >, <, <=, >=
    | \s*(\,)\s*                 # Comma
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
  IS_NUMBER = /^(\-|\+)?([0-9]+(\.[0-9]+)?|Infinity)$/

  LEFT_PAREN  = '('
  RIGHT_PAREN = ')'

  OPS = [ '+', '-', '*', 'div', '=', '!=', '>', '<', '>=', '<=', 'and', 'or', 'not', 'if' ]

  RIGHT_ASSOCIATIVE = [ 'if', 'not', 'selected' ]

  PRECEDENCE =
    '*'   : 6
    'div' : 6
    '+'   : 5
    '-'   : 5
    '='   : 4
    '!='  : 4
    '>'   : 4
    '<'   : 4
    '>='  : 4
    '<='  : 4
    'not' : 3
    'if'  : 2
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
    'not' : (a) -> not a

  MATH =
    '+'   : (x, y) -> x + y
    '-'   : (x, y) -> x - y
    '*'   : (x, y) -> x * y
    'div' : (x, y) -> x / y

  FUNCTIONS =
    'if'  : (x, y, z) -> if x then y else z
    'selected': (actual, expected) ->
      actual = [ actual ] unless actual instanceof Array
      expected in actual

  FUNCTION_ARGS =
    'if'      : 3
    'selected': 2

  # Helper methods for working with expressions
  top = -> this[this.length - 1]

  is_operand = (token) -> OPERAND_REGEX.test token
  is_operator = (token) -> token in OPS
  is_number = (value) -> IS_NUMBER.test(value)
  is_function = (token) -> token in ['if', 'selected']
  is_function_separator = (token) -> token is ','

  precedence = (operator) -> PRECEDENCE[operator]
  right_associative = (operator) -> operator in RIGHT_ASSOCIATIVE
  left_associative = (operator) -> not right_associative(operator)

  parse_boolean = (val) -> if val is 'YES' then true else false

  # Mathematical computation
  compute = (value1, value2, operator) -> MATH[operator] value1, value2

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


  # Convert the expression into an array of tokens
  tokenize = (expression) ->
    # Split the string using our separator regex
    tokens = expression.split(SEPARATOR_REGEX)

    # Split includes 'undefined' for non-matching groups, we don't want that.
    # Remove trailing/leading whitespace and return the tokens.
    ( t.replace /^\s+|\s+$/g, '' for t in tokens when t? and t isnt '' )



  # Convert from infix notation to postfix notation, returning an array of the
  # tokens in postfix order.
  #
  # Parses the tokens using the Shunting-yard algorithm:
  # https://en.wikipedia.org/wiki/Shunting-yard_algorithm
  infix_to_postfix = (tokens) ->
    operator_stack = []
    output  = []
    operator_stack.top = top

    # While there are tokens to be read:
    for token in tokens

      # If the token is an operand, then add it to the output queue.
      if is_operand(token) then output.push token

      # If the token is a function token, then push it onto the stack.
      else if is_function(token) then operator_stack.push token

      # If the token is a function argument separator (ie. a comma):
      else if is_function_separator(token)
        until operator_stack.top() is LEFT_PAREN
          output.push operator_stack.pop()

      # If the token is an operator, T1, then:
      else if is_operator(token)

        # Condition 1: T1 is left-associative and its precedence is less than or equal to that of T2
        condition1 = -> left_associative(token) and precedence(token) <= precedence(operator_stack.top())

        # Condition 2: T1 is right associative, and has precedence less than that of T2
        condition2 = -> right_associative(token) and precedence(token) < precedence(operator_stack.top())

        # While there is an operator token, T2, at the top of the operator
        # stack and either condition 1 or 2 is true, pop T2 off the operator
        # stack, onto the output queue.
        while operator_stack.length > 0 and (condition1() or condition2())
          output.push operator_stack.pop()

        # at the end of the iteration push T1 onto the operator stack.
        operator_stack.push token

      # If the token is "(", then push it onto operator stack.
      else if token is LEFT_PAREN then operator_stack.push token

      # If the token is ")":
      else if token is RIGHT_PAREN

        # Until the token at the top of the stack is a left parenthesis, pop
        # operators off the stack onto the output queue.
        output.push(operator_stack.pop()) until operator_stack.top() is '('

        # Pop the left parenthesis from the stack but not onto the output queue.
        operator_stack.pop()

        # If the token at the top of the stack is a function token, pop it onto
        # the output queue.
        output.push(operator_stack.pop()) if is_function operator_stack.top()

    # When there are no more tokens to read, while there are still operator
    # tokens in the stack, pop the operator onto the output queue.
    until operator_stack.length is 0
      output.push(operator_stack.pop())

    output


  # Evaluate a postfix expression (as an array of tokens) given the currrent
  # field and form responses.
  evaluate_postfix = (tokens, responses, current_field) ->
    output  = []
    output.top = top

    # Convert the token string to the appropriate type.
    process_operand = (token) ->
      val = token

      # If its a selector, e.g. ${foo_field}, get the field value from the form.
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

    # Evaluate a function/operation.
    process_operator = (token) ->
      # If its a function:
      if is_function(token)
        fn = FUNCTIONS[token]
        num_args = FUNCTION_ARGS[token]
        args = ( output.pop() for i in [1..num_args] ).reverse()
        fn(args...)

      # Otherwise its an operator
      else
        operator = token

        # Special case for unary "not" operator.
        if operator is 'not'
          return compare(output.pop(), null, operator)

        # Perform an operation and push the result back on to the operand stack.
        value2 = output.pop()
        value1 = output.pop()
        switch operator
          when '+', '-', '*', 'div'
            value1 = Number.parseFloat value1
            value2 = Number.parseFloat value2
            compute(value1, value2, operator)
          else compare(value1, value2, operator)

    # While there are input tokens left:
    for token in tokens

      # If the token is a value, push it to the stack.
      if is_operand token
        output.push process_operand(token)

      # Otherwise the token is a function or operator, so process it.
      else
        output.push process_operator(token)

    # Return the last value in the output stack.
    output.top()


  class XFormExpression

    #### Public API ####

    @passes_constraint: (field, answers) ->
      return true if not field.bind?.constraint?
      expression = field.bind.constraint
      expression = @_rewrite_expression(expression, answers, field)
      @evaluate(expression, answers, field)


    @is_relevant: (field, answers) ->
      return true if not field.bind?.relevant?
      expression = field.bind.relevant
      expression = @_rewrite_expression(expression, answers, field)
      @evaluate(expression, answers, field)

    @evaluate: (expression, responses, current_field) ->
      tokens = tokenize(expression)
      tokens = infix_to_postfix tokens
      evaluate_postfix tokens, responses, current_field


    #### Private API ####

    # In order to support expressions like if(..) it is easier to tokenize if
    # we rewrite the expression to make certain things like dot operators
    # explicit.
    @_rewrite_expression: (expression, answers, field) ->
      expression = @_replace_dot_shorthand(expression, field.name)
      expression = @_rewrite_not(expression)
      expression = @_rewrite_if(expression)
      expression

    # Replaces instances of the "." shorthand with the current field.
    # e.g. ". >= 0 and . =< 100" => "${grade} >= 0 and ${grade} =< 100"
    @_replace_dot_shorthand: (expr, field) -> expr.replace DOT_SHORTHAND, " ${#{field}} "

    @_rewrite_not: (expr) -> expr.replace /not\(/g, "not ("

    @_rewrite_if: (expr) -> expr.replace /if\(/g, "if ("
