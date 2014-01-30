define( [ 'backbone' ],

( Backbone ) ->

    class VizModel extends Backbone.Model
        url: '/api/v1/viz/'
        sample_url: '/api/v1/data/'

        sample_data: null

        sample: ( callback ) ->

            if @sample_data
                callback( @sample_data )
            else

                sample_url = "/api/v1/data/#{@get('repo')}/sample"
                data =
                    x: @get( 'x_axis' )
                    y: @get( 'y_axis' )

                $.getJSON( sample_url, data, ( data ) =>
                    @sample_data = data
                    callback( data )
                )

            @

    return VizModel

)