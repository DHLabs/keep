define( [ 'backbone' ],

( Backbone ) ->

    class RepoModel extends Backbone.Model

        url: '/api/v1/repos/'

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