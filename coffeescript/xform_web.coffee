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
            @model.fetch( { url: "/api/v1/forms/" + @form_id + "/?user=admin&key=c308c86bd454486273a603b573de4342&format=json" } )

            @

        render: ->

            $( '#xform_debug' ).html( JSON.stringify( @model.attributes ) )

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

            $('#formDiv').html( '' )
            $('#formDiv').html( renderedForm.el )

            @


    App = new xFormView()
