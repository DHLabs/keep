define( [ 'vendor/underscore' ], ( _ ) ->

    build_form = ( child, path, lang ) ->

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
            tree: path

        if child.type in [ 'string', 'text' ]

            if child.bind.readonly
                schema_dict['template'] = _.template( '<div id="<%= editorId %>_field" data-key="<%= editorId %>" class="control-group">
                                                        <strong></strong><%= title %>
                                                   </div>' )
                schema_dict['is_field'] = false

            schema_dict['type'] = 'Text'

        else if child.type in [ 'decimal', 'int', 'integer' ]

            schema_dict['type'] = 'Number'

        else if child.type is 'date'

            schema_dict['type'] = 'Date'

        else if child.type is 'geopoint'

            schema_dict["template"] = _.template( "<div id=\"<%= editorId %>_field\" data-key=\"<%= editorId %>\" class=\"control-group\">          
                                                        <strong></strong><%= title %><br>          
                                                        <input id=\"<%= editorId %>\" type=\"hidden\" name=\"<%= editorId %>\" >          
                                                        <div id=\"map\" style=\"width:100%; height: 500px; position: relative;\"></div>
                                                   </div>")
            schema_dict['bind'] = map: true

        else if child.type is 'today'

            schema_dict['type'] = 'Date'
            schema_dict['title'] = 'Today'

        else if child.type is 'time'

            schema_dict['type'] = 'DateTime'

        else if child.type is 'trigger'

            schema_dict['type'] = 'Checkbox'

        else if child.type is 'note'

            schema_dict['type'] = 'Text'
            schema_dict['template'] = _.template( '<div id="<%= editorId %>_field" data-key="<%= editorId %>" class="control-group">
                                                        <strong></strong><%= title %>
                                                   </div>' )
            schema_dict['is_field'] = false

        else if child.type is 'datetime'

            schema_dict['type'] = 'DateTime'

        else if child.type is 'photo'

            schema_dict['type'] = 'Text'
            schema_dict['template'] = _.template( "<div id='<%= editorId %>_field' data-key='<%= editorId %>' class='control-group'>
                                                        <label for='<%= editorId %>'><%= title %></label>
                                                        <input type='file' name='<%= editorId %>' accept='image/*'></input>
                                                   </div>" )

        else if child.type is 'video'

            schema_dict['type'] = 'Text'
            schema_dict['template'] = _.template( "<div id='<%= editorId %>_field' data-key='<%= editorId %>' class='control-group'>
                                                        <label for='<%= editorId %>'><%= title %></label>
                                                        <input type='file' name='<%= editorId %>' accept='video/*'></input>
                                                   </div>" )

        else if child.type is 'select all that apply'

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

            schema_dict["is_field"] = false
            schema_dict["tree"] = schema_dict["tree"] + (child.name) + "/"
            schema_dict["control"] = child.control
            schema_dict["bind"] = group_start: true
            @item_dict[child.name] = schema_dict
            @_fieldsets.push child.name
            _.each child.children, (_child) ->
                _this.recursiveAdd _child, (schema_dict["tree"])

            return @

        else if child.type is 'select one'

            schema_dict['type'] = 'Select'
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

        else if child.type is 'calculate'

            schema_dict["template"] = _.template(   "<div id=\"<%= editorId %>_field\" data-key=\"<%= editorId %>\" class=\"control-group\">                                                        
                                                        <input id=\"<%= editorId %>\" type=\"hidden\" name=<%= editorId %>
                                                    </div>" )

        else
            schema_dict['type']     = 'Text'
            schema_dict['template'] = _.template( '<div id="<%= editorId %>_field" data-key="<%= editorId %>" class="control-group">
                                                        <label for="<%= editorId %>"><strong>Unsupported:</strong><%= title %></label>
                                                   </div>' )

        @item_dict[child.name] = schema_dict
        @_fieldsets.push( child.name )
        @_data[child.name] = child.default

    return build_form
)
