define( [ 'backbone', 'jquery_cookie' ],

( Backbone ) ->

    class StudyModel extends Backbone.Model

        initialize: ->
            @url = '/api/v1/studies/'

        sync: ( method, model, options ) ->
            options = options || {};

            if method.toLowerCase() in [ 'create' ]
                options.headers = {'X-CSRFToken': $.cookie( 'csrftoken' )}
            else if method.toLowerCase() in [ 'update', 'delete' ]
                options.url = "#{@url}#{model.id}/"
                options.headers = {'X-CSRFToken': $.cookie( 'csrftoken' )}
            else
                options.url = @url

            return Backbone.sync( method, model, options )

)