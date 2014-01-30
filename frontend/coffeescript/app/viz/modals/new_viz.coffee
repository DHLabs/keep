define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'app/models/viz',

          'backbone_modal',
          'jqueryui',
          'jquery_cookie' ],

( $, _, Backbone, Marionette, VizModel ) ->

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
            # - ADD "COUNT" & "TIMESTAMP" TO API

            data =
                name: name
                repo: @repo.id
                x_axis: "data.#{xaxis}"
                y_axis: "data.#{yaxis}"

            new_viz = new VizModel()
            new_viz.save( data, { success: @success_callback } )

            @

    return NewVizModal

)