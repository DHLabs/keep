define( [ 'backbone' ],

( Backbone ) ->

    class DataModel extends Backbone.Model
        defaults:
            data: []

        geopoint: ( field ) ->
            # Converts the specified field(s) into a geopoint
            point = { lat: null, lng: null }

            geojson = @get( 'data' )[ field.name ]

            if not geojson?
                return null

            # Split and convert into lat, lng
            return { lng: geojson.coordinates[0], lat: geojson.coordinates[1] }

    return DataModel

)