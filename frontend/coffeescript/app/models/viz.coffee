define( [ 'backbone', 'jquery_cookie' ],

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

        sync: ( method, model, options ) =>

            options = options || {}
            options.url = "#{@url}#{@get('repo')}/"

            if method.toLowerCase() in [ 'create', 'delete', 'patch', 'update' ]
                options.headers = {'X-CSRFToken': $.cookie( 'csrftoken' )}

            if method.toLowerCase() in [ 'delete' ]
                options.url = "#{@url}#{@get('repo')}/#{options.id}/"

            return Backbone.sync( method, model, options )

    return VizModel

)