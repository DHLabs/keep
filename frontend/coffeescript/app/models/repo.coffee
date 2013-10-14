define( [ 'backbone', 'jquery_cookie' ],

( Backbone ) ->

    class RepoModel extends Backbone.Model

        url: '/api/v1/repos/'

        _detect_fields: ( root, fields ) ->
            for field in root
                if field.type in [ 'group' ]
                    @_detect_fields( field.children, fields )

                # Don't show notes in the raw data table
                if field.type not in [ 'note' ] and field.type not in [ 'group' ]
                    fields.push( field )

        fields: ->
            fields = []
            @_detect_fields( @get( 'children' ), fields )
            return fields

        share: ( options ) ->

            share_url = "/repo/user_share/#{@id}/"

            $.post( share_url,
                    { username: options.data.user, permissions: options.data.perms },
                    ( response ) ->
                        if response == 'success' and options.success?
                            options.success( response )
                        else if options.failure?
                            options.failure( response )
            )

        toJSON: ->
            attrs = _(@attributes).clone()

            # Add ellipsis to repo description if it's too long
            if attrs.description? and attrs.description.length > 0
            	attrs.description = attrs.description[0..42] + '...'

            # Figure out which privacy icon will be shown based on the public/
            # private attributes of the Repository.
            if @get( 'is_public' )
                attrs.privacy_icon = 'icon-unlock'
            else
                attrs.privacy_icon = 'icon-lock'
            return attrs

        sync: ( method, model, options ) ->
            options = options || {};

            if method.toLowerCase() in [ 'patch', 'update', 'delete' ]
                options.url = "#{@url}#{model.id}/"
                options.headers = {'X-CSRFToken': $.cookie( 'csrftoken' )}
            else
                options.url = @url

            return Backbone.sync( method, model, options )


)