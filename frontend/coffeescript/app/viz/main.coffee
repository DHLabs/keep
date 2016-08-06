define( [ 'require' ],
( require ) ->

  require( [ 'app/viz/views', 'jquery', 'underscore', 'backbone' ],
    ( DataVizApp, $, _, Backbone ) ->

      getParameterByName = (name, url) ->
        if not url then url = window.location.href
        name = name.replace(/[\[\]]/g, "\\$&")
        regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)")
        results = regex.exec(url)
        return null if not results
        return '' if not results[2]
        return decodeURIComponent(results[2].replace(/\+/g, " "))

      # Override Backbone.sync to include token auth from querystring with
      # every request.
      do ->
        bb_sync = Backbone.sync

        Backbone.sync = (method, model, options) ->
          options or= {}
          options.dataType = 'json'
          options.data or= {}

          token_auth =
            key: getParameterByName 'key'
            user: 'isn'

          _.extend options.data, token_auth

          bb_sync(method, model, options)

        Backbone.history.start()
        DataVizApp.start()

      # If a patient_id is present in the URL, automatically open the details
      # modal for that patient.
      $( "td:contains('#{document.patient_id}')" ).click() if document.patient_id

      $( '#share_username' ).autocomplete(
        appendTo: '#autofill_list'
        minLength: 1
        source: ( request, response ) ->
          $.ajax(
            url: "/api/v1/user/"
            data:
              username__icontains: $( '#share_username' ).val()
              format: 'json'
            success: ( query ) ->
              response( $.map( query.objects, ( item ) ->
                return { label: item.username, value: item.username }
              ))
          )
      )

      $( '#move_username' ).autocomplete(
        appendTo: '#move_autofill_list'
        minLength: 1
        source: ( request, response ) ->
          $.ajax(
            url: "/api/v1/user/"
            data:
              username__icontains: $( '#move_username' ).val()
              format: 'json'
            success: ( query ) ->
              response ( $.map( query.objects, ( item ) ->
                return { label: item.username, value: item.username }
              ))
          )
      )
  )

)
