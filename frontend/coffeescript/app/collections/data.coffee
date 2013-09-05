define( [
    'backbone',
    'app/models/data' ],

( Backbone, DataModel ) ->

    class DataCollection extends Backbone.Collection
        model: DataModel

        initialize: ( options ) ->
            @url = "/api/v1/data/#{options.repo}/"

        parse: ( response ) ->
            return response.data

        sort: ( options )->
            fetch_data =
                sort: options.field
                sort_type: options.order

            @fetch( { data: fetch_data } )

    return DataCollection
)