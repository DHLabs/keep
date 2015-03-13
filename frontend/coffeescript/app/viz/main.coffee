define( [ 'require' ],
( require ) ->

  require( [ 'app/viz/views', 'jquery', 'jqueryui' ],
    ( DataVizApp, $ ) ->
      Backbone.history.start()
      DataVizApp.start()

      if document.patient_id
        $("td:contains('" +document.patient_id+ "')").click()

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
