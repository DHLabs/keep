define( [ 'vendor/backbone-min' ], ( Backbone ) ->

    class xFormModel extends Backbone.Model

        defaults:
            id: null
            children: []

    return xFormModel
)
