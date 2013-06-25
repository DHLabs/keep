$ ->
    $( '#add_member' ).autocomplete(
        appendTo: '#user_search_list'
        minLength: 2
        source: ( request, response ) ->
            $.ajax(
                url: "/api/v1/user"
                data:
                    format: 'json',
                    username__icontains: request.term
                success: ( data ) ->
                    response( $.map( data.objects, ( item ) ->
                        return { label: item.username, value: item.username }
                    ))
            )
        select: ( event, ui ) ->
            $( '#add_member' ).prop( 'disabled', true )
            member_name = ui.item.value;
            csrftoken = $.cookie( 'csrftoken' )

            $.ajax(
                url: 'member/add/' + member_name + '/'
                type: 'POST'
                beforeSend: ( xhr, settings ) ->
                    xhr.setRequestHeader( 'X-CSRFToken', csrftoken )
                success: ( data ) ->
                    if not data.success
                        return

                    member = _.template( $( '#member_tmpl' ).html() )
                    $( '#member_list' ).append( member( {'member_name': member_name}) )
            )

            $( '#add_member' ).prop( 'disabled', false ).val( '' )
            return false;
    )

    @