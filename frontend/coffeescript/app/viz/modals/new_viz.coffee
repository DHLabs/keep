define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'backbone_modal',
          'jqueryui',
          'jquery_cookie' ],

( $, _, Backbone, Marionette ) ->

    class NewVizModal extends Backbone.Modal
        template: _.template( $( '#new-viz-template' ).html() )
        submitEl: '.btn-primary'
        cancelEl: '.btn-cancel'

        initialize: ( options ) ->
            @fields = options.fields
            @repo   = options.repo

            @success_callback = if options.success? then options.success else null
            @error_callback   = if options.error? then options.error else null

        serializeData: () ->
            return { fields: @fields }

        submit: () ->

            name  = $( '#viz-name', @el ).val()
            xaxis = $( '#xaxis', @el ).val()
            yaxis = $( '#yaxis', @el ).val()

            # TODO:
            # - UPDATE VIZ COLLECTION
            # - ADD "COUNT" & "TIMESTAMP" TO API

            data =
                name: name
                x: "data.#{xaxis}"
                y: "data.#{yaxis}"

            $.ajax(
                url: "/api/v1/viz/#{@repo.get('id')}/"
                data: data
                headers:
                    'X-CSRFToken': $.cookie( 'csrftoken' )
                type: 'POST'
                success: @success_callback
                error: @error_callback
            )

            @

    return NewVizModal

)