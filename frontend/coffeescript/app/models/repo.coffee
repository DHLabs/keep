define( [ 'backbone' ],

( Backbone ) ->

    class RepoModel extends Backbone.Model
        toJSON: ->
            attrs = _(@attributes).clone()

            if @get( 'is_public' )
                attrs.privacy_icon = '<icon class="icon-unlock"></i>'
            else
                attrs.privacy_icon = '<icon class="icon-lock"></i>'
            return attrs

)