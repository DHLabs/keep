define( [ 'underscore' ], ( _ ) ->

    note_tmpl  = _.template('<div id="<%= editorId %>_field" data-key="<%= editorId %>" class="control-group">
                                <strong></strong><%= title %>
                            </div>' )

    photo_tmpl = _.template("<div id='<%= editorId %>_field' data-key='<%= editorId %>' class='control-group'>
                                <label for='<%= editorId %>'><%= title %></label>
                                <input type='file' name='<%= editorId %>' accept='image/*'></input>
                            </div>" )

    video_tmpl = _.template("<div id='<%= editorId %>_field' data-key='<%= editorId %>' class='control-group'>
                                <label for='<%= editorId %>'><%= title %></label>
                                <input type='file' name='<%= editorId %>' accept='video/*'></input>
                            </div>" )

    build_form = ( child, lang ) ->

        label = ''
        if typeof child.label == 'object'
            label = child.label[ lang ]

            if @languages.length == 0
                _.each( child.label, ( child, key ) =>
                    @languages.push( key )
                )
        else
            label = child.label

        schema_dict =
            help: child.hint
            title: label
            is_field: true
            bind: child.bind

        if child.type in [ 'string', 'text', 'note' ]

            schema_dict['type'] = 'Text'

            if child.type is 'note' or ( child.bind? and child.bind.readonly )
                schema_dict['template'] = note_tmpl
                schema_dict['is_field'] = false

        else if child.type in [ 'decimal', 'int', 'integer' ]

            schema_dict['type'] = 'Number'

        else if child.type is 'today'

            schema_dict['type'] = 'Date'
            schema_dict['title'] = 'Today'

        else if child.type in [ 'date', 'time', 'datetime' ]

            schema_dict['type'] = 'DateTime'

        else if child.type is 'trigger'

            schema_dict['type'] = 'Checkbox'

        else if child.type is 'photo'

            schema_dict['template'] = photo_tmpl

        else if child.type is 'video'

            schema_dict['template'] = video_tmpl

        else if child.type in [ 'select all that apply', 'select one' ]

            if child.type is 'select one'
                schema_dict['type'] = 'Select'
            else
                schema_dict['type'] = 'Checkboxes'

            schema_dict['options'] = []

            _.each( child.choices, ( option ) ->

                choice_label = option.label
                if typeof option.label == 'object'
                    choice_label = option.label[ lang ]

                schema_dict['options'].push(
                    val:    option.name
                    label:  choice_label
                )
            )

        else if child.type is 'group'

            _.each( child.children, ( _child ) =>
                @recursiveAdd( _child )
            )

            return @

        else
            schema_dict['type']     = 'Text'
            schema_dict['template'] = _.template( '<div id="<%= editorId %>_field" data-key="<%= editorId %>" class="control-group">
                                                        <label for="<%= editorId %>"><strong>Unsupported:</strong><%= title %></label>
                                                   </div>' )

        @item_dict[ child.name ] = schema_dict
        @_fieldsets.push( child.name )
        @_data[ child.name ] = child.default

    return build_form
)
