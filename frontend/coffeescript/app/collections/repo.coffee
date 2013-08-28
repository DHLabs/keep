define( [ 'backbone' ],

( Backbone ) ->

    class RepoCollection extends Backbone.Collection
        initialize: ->
            @url = '/api/v1/repos/'

        parse: ( response ) ->
            return response.objects

)