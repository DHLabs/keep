define( [ 'backbone' ], ( Backbone ) ->

    class xFormModel extends Backbone.Model

        defaults:
            id: null
            children: []

    return xFormModel
)
