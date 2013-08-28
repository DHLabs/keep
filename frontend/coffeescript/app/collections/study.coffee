define( [ 'backbone' ],

( Backbone ) ->

    class StudyCollection extends Backbone.Collection
        initialize: ->
            @url = '/api/v1/repos/'

        parse: ( response ) ->
            return response.objects

)