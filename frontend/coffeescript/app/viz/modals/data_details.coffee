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
            'geopoint': _.template( '<img src="http://maps.googleapis.com/maps/api/staticmap?
                                        center=<%= data.coordinates[1] %>,<%= data.coordinates[0] %>
                                        &zoom=13
                                        &size=300x100
                                        &maptype=roadmap
                                        &markers=color:red%7C<%= data.coordinates[1] %>,<%= data.coordinates[0] %>
                                        &sensor=false">' )

            'photo':    _.template( '<img style="max-width:300px;" src="<%= data %>" >'  )

        initialize: ( options ) ->
            @model  = options.model
            @fields = options.fields
            @repo   = options.repo
            @linked = options.linked

        onAfterRender: (modal) ->
            document.data_id = @model.attributes.id
            document.data_detail = @model.attributes.data
            $( '#edit_data_btn', modal ).click( @editData )
            $( '#delete_data_btn', modal ).click( @deleteData )
            @

        editData: (event) ->
            new_location = '/' + document.repo_owner + '/' +
                document.repo.name + '/webform/?data_id=' + document.data_id

            for key in _.keys(document.data_detail)
                new_location += '&' + key + '='
                #TODO: replace spaces and ampersands in detail string
                new_location += document.data_detail[key]
                
            window.location = new_location
            @

        deleteData: (event) ->
            the_url = '/api/v1/data/' + document.repo.id + '/?data_id=' + document.data_id
            $.ajax({ 
                url: the_url,
                type:'DELETE', 
                headers: {
                    'X-CSRFToken': $.cookie( 'csrftoken' )
                }
                })
            .done(
                () ->
                    location.reload()
            )
            @

        serializeData: () ->
            # Loop through each data pair and formalize
            attributes = {}
            filter = null

            for field in @fields
                tdata = { data: @model.attributes.data[ field.name ] }

                if field.type in [ 'geopoint', 'photo' ]
                    if tdata['data']
                        attributes[ field.name ] = @data_templates[ field.type ]( tdata )
                    else
                        attributes[ field.name ] = @data_templates[ 'text' ]( tdata )
                else
                    attributes[ field.name ] = @data_templates[ 'text' ]( tdata )

                if field.name == 'patient_id'
                    filter = attributes[ field.name ]

            data =
                model: @model
                attributes: attributes
                can_continue: @model.attributes.can_continue
                is_tracker: @repo.get( 'is_tracker' )
                linked: @linked.models
                filter: filter

            return data

    return DataDetailsModal

)