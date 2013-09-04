define( [
    'backbone',
    'app/models/data' ],

( Backbone, DataModel ) ->

    class DataCollection extends Backbone.Collection
        model: DataModel

        parse: ( response ) ->
            return response.data

        sort: ( options )->
            if not options.repo?
                return

            @url = "/api/v1/data/#{options.repo}/"

            fetch_data =
                sort: options.field
                sort_type: options.order

            @fetch( { data: fetch_data } )

    return DataCollection
)