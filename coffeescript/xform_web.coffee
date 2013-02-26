# TODO
#   - Handle xform bindings
#       - Required
#       - Constraints
#       - etc
#
#

$ ->
    mobileView = false
    _fieldsets = []
    _schema = {}
    _data = {}
    item_dict = {}
    swipeFrame = null

    # Rendered form values will be handled with this variable
    renderedForm = null


    class xFormModel extends Backbone.Model

        defaults:
            id: null
            children: []


    class xFormView extends Backbone.View

        # The HTML element where the form will be rendered
        el: $( '#xform_view' )

        # Current form this view is representing
        model: new xFormModel()

        events:
            'click #submit-xform': 'validate'

        initialize: ->
            # Grab the form_id from the page
            @form_id = $( '#form_id' ).html()

            # Begin render when the model is finished fetching from the server
            @listenTo( @model, 'change', @render )
            @model.fetch( { url: "/api/v1/forms/" + @form_id + "/?user=admin&key=35ec69714b23a33e79b0d859f51fa458&format=json" } )

            @

        passesConstraint: ( question, answers ) ->
            passesConstraint = true
            if question.bind and question.bind.constraint
                constraint = question.bind.constraint
                expression = @evaluateSelectedInExpression(constraint, answers, question["name"])
                return @evaluateExpression(expression, answers, question["name"])

            return passesConstraint

        isRelevant: (question, answers) ->
            containsRelevant = question.bind and question.bind.relevant
            if containsRelevant
                relevantString = question.bind.relevant
                expression = relevantString.replace /\./, question["name"]
                expression = @evaluateSelectedInExpression(expression, answers, question["name"])
                return @evaluateExpression(expression, answers, question["name"])
            else
                return true

         # Function replaces all "selected(.,'foo')" with evaluated boolean of YES or NO
        evaluateSelectedInExpression: (expression, answers, currentPath) ->
            keepGoing = true
            string = expression

            while keepGoing
                range = expression.indexOf "selected("

                if range != -1
                    substring = expression[(range + 9) .. ]
                    endRange = substring.indexOf ")"
                    selected = substring[0 .. endRange]

                    components = selected.split ","

                    # check for answer
                    leftString = components[0].replace /^\s+|\s+$/g, ""
                    rightString = components[0].replace /^\s+|\s+$/g, ""

                    if leftString is "."
                        leftString = currentPath

                    # remove quotes from rightstring
                    rightString = rightString[1 .. rightString.length - 2]

                    answer = answers[leftString]

                    replaceString = expression[range .. endRange]
                    if answer is rightString
                        string = string.replace replaceString, "YES"
                    else
                        string = string.replace replaceString, "NO"
                else
                    keepGoing = false
            return string

        # function recursively breaks down logical expression for individual evaluation and then reconstruction back up the tree
        evaluateExpression: (expression, answers, currentPath) ->
            # evaluate all selected
            scopeRange = expression.indexOf "("
            andRange = expression.indexOf " and "
            orRange = expression.indexOf " or "
            notRange = expression.indexOf "not(", 0

            range = scopeRange
            rangeLength = 1

            if andRange != -1 and andRange < range
                range = andRange
                rangeLength = 5

            if orRange != -1 and orRange < range
                range = orRange
                rangeLength = 4

            if notRange != -1 and notRange < range
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
                            return (@evaluateExpression(parentrString, answers, currentPath) or evaluateExpression(leftOverString, answers, currentPath))
                        else if andLocation != 0
                            return (@evaluateExpression(parentrString, answers, currentPath) and evaluateExpression(leftOverString, answers, currentPath))
                        else if andLocation != -1 or orLocation != -1
                            return @evaluateExpression(parentString, answers, currentPath)
                    else
                        return @evaluateExpression(parentString, answers, currentPath)
                else if range == andRange
                    leftExpression = expression[0 .. range]
                    rightExpression = expression[(range + rangeLength) .. ]
                    return (@evaluateExpression(leftExpression, answers, currentPath) and evaluateExpression(rightExpression, answers, currentPath))
                else if range == orRange
                    leftExpression = expression[0 .. range]
                    rightExpression = expression[(range + rangeLength) .. ]
                    return (@evaluateExpression(leftExpression, answers, currentPath) or evaluateExpression(rightExpression, answers, currentPath))
                else if range == notRange
                    closeRange = expression.lastIndexOf ")"
                    newExpression = expression[(range + rangeLength) .. (closeRange - (range + rangeLength))]
                    return not(@evaluateExpression(newExpression, answers, currentPath))
            else
                return @passesTest(expression, answers, currentPath)

            return true

        # This function evaluates the base logical expression i.e. ( x != y ), no and's, or's, or not's anymore at this level
        passesTest: (expression, answers, currentPath) ->
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

            leftString = comps[0].replace /^\s+|\s+$/g, ""

            if leftString is "."
                leftString = currentPath

            rightString = comps[1].replace /^\s+|\s+$/g, ""

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
                    rightAnswer = ((rightAnswer.split "'")[1]).replace /^\s+|\s+$/g, ""

                    if compareString is "="
                        return leftAnswer is rightAnswer
                    else if compareString is "!="
                        return leftAnswer isnt rightAnswer
                    else
                        # shouldn't get here
                        return false

        render: ->

            #$( '#xform_debug' ).html( JSON.stringify( @model.attributes ) )
                    
            if mobileView
                @loadMobileForm()
            else
                @loadForm()

            @

        validate: ->
            console.log( renderedForm.getValue() )

            posted_data =
                form: @form_id
                values: renderedForm.getValue()

            console.log( posted_data )
           
            $.post( '/submission', posted_data, null )

        
        recursiveAdd: ( child ) ->

            schema_dict =
                help: child.hint
                title: child.label


            if _fieldsets.length is 0 and mobileView
                schema_dict['template'] = 'firstField'


            if child.type in [ 'string', 'text' ]

                schema_dict['type'] = 'Text'

            else if child.type in [ 'decimal', 'int', 'integer' ]

                schema_dict['type'] = 'Number'

            else if child.type is 'date'

                schema_dict['type'] = 'Date'

            else if child.type is 'today'

                schema_dict['type'] = 'Date'
                schema_dict['title'] = 'Today'

            else if child.type is 'time'

                schema_dict['type'] = 'DateTime'

            else if child.type is 'trigger'

                schema_dict['type'] = 'Checkbox'

            else if child.type is 'note'

                schema_dict['type'] = 'Text'
                schema_dict['template'] = 'noteField'

            else if child.type is 'datetime'

                schema_dict['type'] = 'DateTime'

            else if child.type is 'select all that apply'

                schema_dict['type'] = 'Checkboxes'
                schema_dict['options'] = []

                _.each( child.choices, ( option ) ->
                    schema_dict['options'].push(
                        val:    option.name
                        label:  option.label
                    )
                )

            else if child.type is 'group'
                # this is a hack
                schema_dict['type'] = 'Text'
                schema_dict['template'] = 'groupBegin'

                _.each( child.children, ( _child ) =>
                    @recursiveAdd( _child )
                )

                schema_dict =
                    type:       'Text'
                    help:       child.hint
                    title:      child.label
                    template:   'groupEnd'

                item_dict[child.name + '-end'] = schema_dict
                _fieldsets.push(child.name + '-end')

                return @

            else if child.type is 'select one'

                schema_dict['type'] = 'Select'
                schema_dict['options'] = []

                _.each( child.choices, ( option ) ->
                    schema_dict['options'].push(
                        val:    option.name
                        label:  option.label
                    )
                )

            else
                schema_dict['type']     = 'Text'
                schema_dict['template'] = 'unsupportedField'

            item_dict[child.name] = schema_dict
            _fieldsets.push( child.name )
            _data[child.name] = child.default

            @

        loadMobileForm: () ->
            _fieldsets = []
            _schema = {}
            _data = {}
            item_dict = {}
            swipeFrame = null

            $( document ).bind( 'touchmove', ( e ) ->
                e.preventDefault()
            )

            Backbone.Form.setTemplates(
                fieldset: '<ul>{{fields}}</ul'
                customForm: '<div id="slider2" class="swipe">{{fieldsets}}</div>'
                field: '<li style="display:none;"><label for="{{id}}">{{title}}</label><div>{{editor}}</div><div>{{help}}</div></li>'
                unsupportedField: '<li style="display:none;"><label for="{{id}}">{{title}}</label></li>'
                firstField: '<li style="display:block;"><label for="{{id}}">{{title}}</label><div>{{editor}}</div><div>{{help}}</div></li>'
                noteField: '<li style="display:none;"><label class="control-label" for="{{id}}">{{title}}</label></div></li>'
                groupBegin: '<li style="display:none;"><div class="well"><div><strong>Group: </strong>{{title}}</div></div></li>'
                groupEnd: '<li style="display:none;"><div><strong>Group End: </strong>{{title}}<hr></div></li>'
            )

            _.each( @model.attributes.children, ( child ) =>
                @recursiveAdd( child )
            )

            renderedForm = new Backbone.Form(
                template: 'customForm'
                schema: item_dict
                data: _data
                fields: _fieldsets
            ).render()

            $('#formDiv').html( '' )
            $('#formDiv').html( renderedForm.el )

            swipeFrame = new Swipe( document.getElementById('slider2') )

            @

        loadForm: () ->
            _fieldsets = []
            _schema = {}
            _data = {}
            item_dict = {}
            swipeFrame = null

            Backbone.Form.setTemplates(
                unsupportedField: '<div class="control-group"><label for="{{id}}"><strong>Unsupported:</strong> {{title}}</label></div>'
                noteField: '<div class="control-group"><strong>Note: </strong>{{title}}</div>'
                groupBegin: '<div class="well"><div><strong>Group: </strong>{{title}}</div></div>'
                groupEnd: '<div><hr></div>'
            )

            _.each( @model.attributes.children, ( child ) =>
                @recursiveAdd( child )
            )

            renderedForm = new Backbone.Form(
                schema: item_dict
                data:   _data
                fields: _fieldsets
            ).render()

	    #debugger
            answers = renderedForm.getValue()

            # check and display relevance as debug output
            relevance = ( for child in @model.attributes.children
                child.name + ":" + @isRelevant( child, answers )
            )
               
            $( '#xform_debug' ).html( JSON.stringify( relevance ) )

            $('#formDiv').html( '' )
            $('#formDiv').html( renderedForm.el )

            @


    App = new xFormView()
