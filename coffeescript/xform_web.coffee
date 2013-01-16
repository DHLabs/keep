$ ->
    mobileView = false
    getForm = null
    _fieldsets = []
    _schema = {}
    _data = {}
    item_dict = {}
    swipeFrame = null


    class xFormModel extends Backbone.Model

        defaults:
            id: null
            children: []


    class xFormView extends Backbone.View

        # The HTML element where the form will be rendered
        el: $( '#xform_view' )

        # Current form this view is representing
        model: new xFormModel()

        initialize: ->
            # Begin render when the model is finished fetching from the server
            @listenTo( @model, 'change', @render )
            @model.fetch( { url: "/api/v1/forms/50ca6a9ca14cd282229139fa/?user=admin&key=c308c86bd454486273a603b573de4342&format=json" } )

            @

        render: ->

            if mobileView
                @loadMobileForm()
            else
                @loadForm()

            @

        recursiveAdd: ( child ) ->

            schema_dict = {}
            schema_dict['help'] = child.hint
            schema_dict['title'] = child.label

            if _fieldsets.length is 0 and mobileView
                schema_dict['template'] = 'firstField'


            if child.type in [ 'string', 'text' ]

                schema_dict['type'] = 'Text'

            else if child.type in [ 'int', 'integer' ]

                schema_dict['type'] = 'Number'

            else if child.type is 'decimal'

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
                option_array = []

                _.each( child.choices, ( option ) ->

                    option_array.push(
                        val:    option.name
                        label:  option.label
                    )

                )

                schema_dict['options'] = option_array

            else if child.type is 'group'
                # this is a hack
                schema_dict['type'] = 'Text'
                schema_dict['template'] = 'groupBegin'

                _.each( child.children, ( _child ) =>
                    @recursiveAdd( _child )
                )

                schema_dict = {};
                schema_dict['type'] = 'Text';
                schema_dict['help'] = child.hint
                schema_dict['title'] = child.label
                schema_dict['template'] = 'groupEnd'

                item_dict[child.name + '-end'] = schema_dict
                _fieldsets.push(child.name + '-end')

                return @

            else if child.type is 'select one'

                schema_dict['type'] = 'Select'

                option_array = []

                _.each( child.choices, ( option ) ->

                    option_array.push(
                        val:    option.name
                        label:  option.label
                    )
                )

                schema_dict['options'] = option_array;

            else

                schema_dict['type'] = 'Text';
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

            getForm = new Backbone.Form(
                template: 'customForm'
                schema: item_dict
                data: _data
                fields: _fieldsets
            )
            getForm.render()

            $('#formDiv').html("")
            $('#formDiv').html(getForm.el)

            swipeFrame = new Swipe(document.getElementById('slider2'))
            console.log(swipeFrame)

            @

        loadForm: () ->
            _fieldsets = []
            _schema = {}
            _data = {}
            item_dict = {}
            swipeFrame = null

            Backbone.Form.setTemplates(
                unsupportedField: '<div><label for="{{id}}"><strong>Unsupported:</strong> {{title}}</label></div>'
                noteField: '<div><strong>Note: </strong>{{title}}</div>'
                groupBegin: '<div class="well"><div><strong>Group: </strong>{{title}}</div></div>'
                groupEnd: '<div><hr></div>'
            )

            _.each( @model.attributes.children, ( child ) =>
                @recursiveAdd( child )
            )

            getForm = new Backbone.Form(
                schema: item_dict
                data:   _data
                fields: _fieldsets
            ).render()

            $('#formDiv').html("")
            $('#formDiv').html(getForm.el)

            @

    App = new xFormView()
