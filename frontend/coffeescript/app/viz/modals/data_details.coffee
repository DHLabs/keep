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

        events:
          'click .js-show-data': 'show_repo'
          'click .js-add-data': 'add_data'

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

        # Redirect to appropriate repo with query params
        add_data: (event) ->
          event.preventDefault()
          base_url = event.target.href
          context = window.location.search
          window.location = base_url + context

        # Redirect to appropriate repo with query params
        show_repo: (event) ->
          event.preventDefault()
          base_url = event.target.href
          context = window.location.search
          window.location = base_url + context

        # Reroute to the webform for editing
        editData: (event) ->
          event.preventDefault()
          base_url = "/#{document.repo_owner}/#{document.repo.name}/webform/?"
          data = _.extend {data_id: document.data_id}, document.data_detail
          window.location = base_url + $.param(data)


        deleteData: (event) ->
          event.preventDefault()

          url = "/api/v1/data/#{document.repo.id}/?data_id=#{document.data_id}"
          # add the token auth but slice off the '?'
          url += ("&" + window.location.search.slice(1))

          request = $.ajax
            url: url,
            type: 'DELETE',
            headers: 'X-CSRFToken': $.cookie('csrftoken')

          # Reload the page once the item has been deleted.
          request.done -> location.reload()


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

                if field.name is 'patient_id'
                    filter = attributes[ field.name ]

            data =
                attributes: attributes
                is_tracker: @repo.get( 'is_tracker' )
                linked: @linked.models
                filter: filter

            return data

    return DataDetailsModal

)
