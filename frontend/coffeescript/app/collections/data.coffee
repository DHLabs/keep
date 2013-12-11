define( [
    'underscore',
    'backbone',
    'app/models/data' ],

( _, Backbone, DataModel ) ->

    class DataCollection extends Backbone.Collection
        model: DataModel

        initialize: ( options ) ->
            @url = "/api/v1/data/#{options.repo.id}/"
            @meta =
                offset: 0

        comparator: ( data ) ->
            return data.get( 'timestamp' )

        next: ( options ) ->
            # Set up the page offset
            data = {}
            data.offset = @meta.offset + 1

            # Don't load new offsets if we already have all the pages.
            if @meta.pages? and data.offset > @meta.pages
                return

            # Also add sort details if the list is sorted
            if @sort_data?
                data.sort = @sort_data.sort
                data.sort_type = @sort_data.sort_type

            # We want to add the additional models and not remove any.
            options = _.extend( { data: data, add: true, remove: false }, options )
            @fetch( options )

        parse: ( response ) ->
            # Save metadata info returned by API call
            @meta = response.meta if response.meta?
            return response.data

        sort_fetch: ( options )->
            @sort_data =
                sort: options.field
                sort_type: options.order
            @fetch( { data: @sort_data, reset: true } )

        stats: ( options ) ->
            # Return stats about this data collection
            # TODO!
            stats_url = "{@url}stats/"

    return DataCollection
)