define( [ 'backbone' ],

( Backbone ) ->

    class DataModel extends Backbone.Model
        defaults:
            data: []

        geopoint: ( field ) ->
            # Converts the specified field(s) into a geopoint
            point = { lat: null, lng: null }

            geostring = @get( 'data' )[ field.name ]

            if not geostring?
                return null

            # Split and convert into lat, lng
            geostring = geostring.split( ' ' )[0..2]

            point.lat = parseFloat( geostring[0] )
            point.lng = parseFloat( geostring[1] )

            if isNaN( point.lat ) or isNaN( point.lng )
                return null

            return point

    return DataModel

)