define( [
    'backbone',
    'app/models/data' ],

( Backbone, DataModel ) ->

    class DataCollection extends Backbone.Collection
        model: DataModel

        initialize: ->
            # Grab the form_id from the page
            @form_id = $( '#form_id' ).html()
            @url = "/api/v1/data/#{@form_id}/?format=json"

        comparator: ( data ) ->
            return data.get( 'timestamp' )

    return DataCollection
)