define( [ 'backbone' ],

( Backbone ) ->

    class RepoModel extends Backbone.Model
        toJSON: ->
            attrs = _(@attributes).clone()

            # Add ellipsis to repo description if it's too long
            if attrs.description? and attrs.description.length > 0
            	attrs.description = attrs.description[0..42] + '...'

            # Figure out which privacy icon will be shown based on the public/
            # private attributes of the Repository.
            if @get( 'is_public' )
                attrs.privacy_icon = '<icon class="icon-unlock"></i>'
            else
                attrs.privacy_icon = '<icon class="icon-lock"></i>'
            return attrs

)