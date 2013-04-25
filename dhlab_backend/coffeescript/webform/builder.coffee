define( [ 'vendor/underscore' ], ( _ ) ->

    build_form = ( child ) ->
        schema_dict =
            help: child.hint
            title: child.label
            is_field: true
            bind: child.bind

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
            schema_dict['template'] = _.template( '<div id="<%= editorId %>_field" class="control-group"><strong>Note: </strong><%= title %></div>' )
            schema_dict['is_field'] = false

        else if child.type is 'datetime'

            schema_dict['type'] = 'DateTime'

        else if child.type is 'photo'

            schema_dict['type'] = 'Text'
            schema_dict['template'] = _.template( "<div id='<%= editorId %>_field' class='control-group'><label for='<%= editorId %>'><%= title %></label><input type='file' accept='image/png'></input></div>" )

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

            _.each( child.children, ( _child ) =>
                @recursiveAdd( _child )
            )

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
            schema_dict['template'] = _.template( '<div id="<%= editorId %>_field" class="control-group"><label for="<%= editorId %>"><strong>Unsupported:</strong><%= title %></label></div>' )

        @item_dict[child.name] = schema_dict
        @_fieldsets.push( child.name )
        @_data[child.name] = child.default

    return build_form
)
