define( [ 'backbone',
          'app/models/study' ],

( Backbone, StudyModel ) ->

    class StudyCollection extends Backbone.Collection
        model: StudyModel
        url: '/api/v1/studies/'

        parse: ( response ) ->
            return response.objects

    return StudyCollection
)