define( [
    'underscore',
    'backbone',
    'app/models/viz' ],

( _, Backbone, VizModel ) ->

    class VizCollection extends Backbone.Collection
        model: VizModel

        parse: ( response ) ->
          return response.objects

    return VizCollection
)
