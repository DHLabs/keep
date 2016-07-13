define( [
    'backbone',
    'app/models/repo' ],

( Backbone, RepoModel ) ->

    class RepoCollection extends Backbone.Collection
        model: RepoModel
        url: '/api/v1/repos/'

        parse: ( response ) ->
            return response.objects

)