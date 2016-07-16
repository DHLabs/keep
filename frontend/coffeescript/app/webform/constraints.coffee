define( [], ->

	class XFormConstraintChecker

		@passesConstraint: ( question, answers ) ->
            passesConstraint = true
            if question.bind and question.bind.constraint
                constraint = question.bind.constraint
                expression = @evaluateSelectedInExpression(constraint, answers, question["name"])
                return @evaluateExpression(expression, answers, question["name"])

            return passesConstraint

        @isRelevant: (question, answers) ->
            containsRelevant = question.bind and question.bind.relevant

            if containsRelevant
                relevantString = question.bind.relevant
                expression = relevantString.replace /\./, question["name"]
                expression = @evaluateSelectedInExpression(expression, answers, question["name"])
                return @evaluateExpression(expression, answers, question["name"])
            else
                return true

        # Function replaces all "selected(.,'foo')" with evaluated boolean of YES or NO
        @evaluateSelectedInExpression: (expr, answers, currentPath) ->
            expression = expr

            while true
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
                field_name = "${#{currentPath}}" if field_name is "."

                # Remove ${} from field name, and quotes from expected value and
                # trim whitespace.
                field_name = field_name.replace /\s+/g, ""
                field_name = field_name[2 .. field_name.length - 2]
                expected_value = expected_value.replace /\s+/g, ""
                expected_value = expected_value[1 .. expected_value.length - 2]

                # Replace the "selected(...)" expression with YES or NO.
                answer = answers[field_name]
                expr = expression[start_range .. end_range]
                result = if answer is expected_value then 'YES' else 'NO'
                expression = expression.replace expr, result

            return expression

        # function recursively breaks down logical expression for individual
        # evaluation and then reconstruction back up the tree
        @evaluateExpression: (expression, answers, currentPath) ->
            # evaluate all selected
            scopeRange = expression.indexOf "("
            andRange = expression.indexOf " and "
            orRange = expression.indexOf " or "
            notRange = expression.indexOf "not(", 0

            range = scopeRange
            rangeLength = 1

            if andRange != -1 and andRange > range
                range = andRange
                rangeLength = 5

            if orRange != -1 and orRange > range
                range = orRange
                rangeLength = 4

            if notRange != -1 and notRange > range
                range = notR
                rangeLength = 4

            if range != -1
                if range == scopeRange
                    closeRange = expression.lastIndexOf ")"
                    parentString = expression[(range + 1) .. (closeRange - range - 2)]

                    if closeRange < (expression.length - 1)
                        leftOverString = expression[(closeRange + 1) .. ]
                        orLocation = leftOverString.indexOf " or "
                        andLocation = leftOverString.indexOf " and "

                        if orLocation != 0
                            return (@evaluateExpression(parentString, answers, currentPath) or @evaluateExpression(leftOverString, answers, currentPath))
                        else if andLocation != 0
                            return (@evaluateExpression(parentrString, answers, currentPath) and @evaluateExpression(leftOverString, answers, currentPath))
                        else if andLocation != -1 or orLocation != -1
                            return @evaluateExpression(parentString, answers, currentPath)
                    else
                        return @evaluateExpression(parentString, answers, currentPath)
                else if range == andRange
                    leftExpression = expression[0 .. range]
                    rightExpression = expression[(range + rangeLength) .. ]
                    return (@evaluateExpression(leftExpression, answers, currentPath) and @evaluateExpression(rightExpression, answers, currentPath))
                else if range == orRange
                    leftExpression = expression[0 .. range]
                    rightExpression = expression[(range + rangeLength) .. ]
                    return (@evaluateExpression(leftExpression, answers, currentPath) or @evaluateExpression(rightExpression, answers, currentPath))
                else if range == notRange
                    closeRange = expression.lastIndexOf ")"
                    newExpression = expression[(range + rangeLength) .. (closeRange - (range + rangeLength))]
                    return not(@evaluateExpression(newExpression, answers, currentPath))
            else
                return @passesTest(expression, answers, currentPath)

            return true

        # This function evaluates the base logical expression i.e. ( x != y ),
        # no and's, or's, or not's anymore at this level
        @passesTest: (expression, answers, currentPath) ->
            # evalaute the equality
            if expression is "YES"
                return true
            else if expression is "NO"
                return false

            if (expression.indexOf "<=") != -1
                compareString = "<="
            else if (expression.indexOf ">=") != -1
                compareString = ">="
            else if (expression.indexOf "!=") != -1
                compareString = "!="
            else if (expression.indexOf "=") != -1
                compareString = "="
            else if (expression.indexOf "<") != -1
                compareString = "<"
            else if (expression.indexOf ">") != -1
                compareString = ">"
            else
                # No comparison string found, Should not happen.
                return true

            comps = expression.split compareString

            leftString = comps[0].replace /\s+/g, ""

            if leftString is "."
                leftString = "${" + currentPath + "}"

            rightString = comps[1].replace /\s+/g, ""

            leftAnwer = null
            rightAnswer = null

            # check if leftString is a path to question
            if (leftString.indexOf "$") != -1
                lName = leftString[2...(leftString.length - 1)]
                leftAnswer = answers[lName]

                if leftAnswer instanceof Array
                    leftAnswer = "''"
            else
                # left string is not a path, return false
                return false

            if (rightString.indexOf "$") != -1
                rName = rightString[2...(rightString.length - 1)]
                rightAnswer = answers[rName]

                if rightAnswer instanceof Array
                    rightAnswer = "''"
            else
                rightAnswer = rightString

            # null cases
            if leftAnswer is null or rightAnswer is null
                if leftAnswer isnt null
                    if compareString is "!="
                        return true
                else if rightAnswer isnt null
                    if compareString is "!=" and rightAnswer is "''"
                        return false
                    else if compareString is "=" and rightAnswer is "''"
                        return true
                    else if compareString is "!="
                        return true
                else
                    if compareString is "="
                        return true
                return false

            # evaluate the expression

            # special function cases
            if rightAnswer is "today()"
                # do the date comparison stuff
                return false
            else
                number = parseInt(rightAnswer)

                if not(isNaN(number))

                    leftFloat = parseFloat(leftAnswer)
                    rightFloat = parseFloat(rightAnswer)
                    if compareString is "<"
                        return leftFloat < rightFloat
                    else if compareString is ">"
                        return leftFloat > rightFloat
                    else if compareString is "="
                        return leftFloat == rightFloat
                    else if compareString is "<="
                        return leftFloat <= rightFloat
                    else if compareString is ">="
                        return leftFloat >= rightFloat
                    else
                        return leftFloat != rightFloat
                else
                    # if it's not a number, then it should be a selection choice (string)
                    # string comparisons are only equal or not equal

                    # remove surrounding quotes
                    if "'" in rightAnswer
                        rightAnswer = ((rightAnswer.split "'")[1]).replace /\s+/g, ""

                    if "\"" in rightAnswer
                        rightAnswer = ((rightAnswer.split "\"")[1]).replace /\s+/g, ""

                    if compareString is "="
                        return leftAnswer is rightAnswer
                    else if compareString is "!="
                        return leftAnswer isnt rightAnswer
                    else
                        # shouldn't get here
                        return false
)
