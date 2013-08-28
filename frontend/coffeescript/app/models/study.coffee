define( [ 'backbone', 'jquery_cookie' ],

( Backbone ) ->

    class StudyModel extends Backbone.Model

        initialize: ->
            @url = '/api/v1/studies/'

        sync: ( method, model, options ) ->
            options = options || {};

            if method.toLowerCase() in [ 'update', 'delete' ]
                options.url = "#{@url}#{model.id}/"
                options.headers = {'X-CSRFToken': $.cookie( 'csrftoken' )}
            else
                options.url = @url

            console.log( @url )
            console.log( options )

            return Backbone.sync( method, model, options )

)