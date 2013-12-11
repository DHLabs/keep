define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'backbone_modal',
          'jqueryui' ],

( $, _, Backbone, Marionette ) ->

    class DataDetailsModal extends Backbone.Modal
        template: _.template( $( '#data-detail-template' ).html() )
        cancelEl: '.btn-primary'

        data_templates:
            'text':     _.template( '<%= data %>' )
            'geopoint': _.template( '<%= data.coordinates[1] %>, <%= data.coordinates[0] %>' )
            'photo':    _.template( '<img src="<%= data %>" >'  )

        initialize: ( options ) ->
            @model = options.model
            @fields = options.fields

        serializeData: () ->
            # Loop through each data pair and formalize
            attributes = {}
            for field in @fields
                tdata = { data: @model.attributes.data[ field.name ] }

                if field.type in [ 'geopoint', 'photo' ]
                    attributes[ field.name ] = @data_templates[ field.type ]( tdata )
                else
                    attributes[ field.name ] = @data_templates[ 'text' ]( tdata )

            data =
                attributes: attributes

            return data

    return DataDetailsModal

)