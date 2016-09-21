define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'backbone_modal',
          'jqueryui' ],

( $, _, Backbone, Marionette ) ->

    # TODO duplicated in viz/main.coffee, extract to utils file.
    getParameterByName = (name, url) ->
      if not url then url = window.location.href
      name = name.replace(/[\[\]]/g, "\\$&")
      regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)")
      results = regex.exec(url)
      return null if not results
      return '' if not results[2]
      return decodeURIComponent(results[2].replace(/\+/g, " "))

    get_auth_context = ->
      auth_keys = ['key', 'user', 'provider_id', 'cluster_id']
      context = {}
      context[key] = getParameterByName(key) for key in auth_keys
      context

    class DataDetailsModal extends Backbone.Modal
        template: _.template $('#data-detail-template').html()
        cancelEl: '.js-cancel'

        events:
          'click .js-show-data': 'show_repo'
          'click .js-add-data': 'add_data'
          'click .js-edit': 'edit_data'
          'click .js-delete': 'delete_data'

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

        # Redirect to appropriate repo with query params
        add_data: (event) =>
          event.preventDefault()
          base_url = event.target.href

          # Get patient ID and auth query params
          context = get_auth_context()
          context.patient_id = @model.get('data').patient_id

          window.location = base_url + '?' + $.param(context)

        # Redirect to appropriate repo with query params
        show_repo: (event) =>
          event.preventDefault()
          base_url = event.target.href

          # Get patient ID and auth query params
          context = get_auth_context()
          context.patient_id = @model.get('data').patient_id

          window.location = base_url + '?' + $.param(context)

        # Reroute to the webform for editing
        edit_data: (event) =>
          event.preventDefault()
          base_url = "/#{document.repo_owner}/#{document.repo.name}/webform/?"
          context = get_auth_context()
          context = _.extend context, @model.get 'data'
          context.data_id = @model.get 'id'
          delete context['_status']
          window.location = base_url + $.param(context)


        delete_data: (event) =>
          event.preventDefault()

          url = "/api/v1/data/#{document.repo.id}/?"
          context = get_auth_context()
          context.data_id = @model.get('id')
          url += $.param(context)

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
