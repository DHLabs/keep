define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'backbone_modal',
          'jqueryui' ],

( $, _, Backbone, Marionette ) ->

    class ShareSettingsModal extends Backbone.Modal
        template: _.template( $( '#sharing-settings' ).html() )
        cancelEl: '.btn-primary'

        shared_user: _.template(
            '''
                <tr data-user='<%= user %>'>
                    <td><%= user %></td>
                    <td><%= perm %></td>
                    <td style='text-align:center'>
                        <a href='#' class='btn-delete'>
                            <i class='fa fa-trash'></i>
                        </a>
                    </td>
                </tr>
            ''' )

        initialize: ( options ) ->
            @repo = options.repo

        beforeSubmit: ->
            # Prevent the "submit" action ( ENTER ) since people may using that
            # with the autocomplete boxes in the modal.
            return false

        onAfterRender: ( modal ) ->
            $( '#add-share', modal ).click( @add_share )

            $( '#sharing-user' ).autocomplete(
                appendTo: '#sharing_user_list'
                minLength: 2
                source: @autocomplete_source
                autoFocus: true
                focus: ( event, ui ) ->
                    $( '.ui-state-selected' ).removeClass( 'ui-state-selected' )
                    li = $( '.ui-state-focus', event.currentTarget ).parent()
                    li.addClass( 'ui-state-selected' )
            )

            $( '.btn-delete', modal ).click( @remove_share )

            $( '#sharing_toggle' ).change( @toggle_public )
            $( '#form_access_toggle' ).change( @toggle_form_public )

            @

        add_share: ( event ) =>
            user  = $( '#sharing-user' ).val()
            perms = $( '#sharing-perms' ).val()

            @repo.share(
                data:
                    user: user
                    perms: perms
                success: ( response ) =>
                    $( '#shared-users-list' ).append( @shared_user( {user: user, perm: perms} ) )
                    $('.btn-delete').click( @remove_share )
            )
            @

        autocomplete_source: ( request, response ) ->
            $.ajax
              url: "/api/autocomplete/accounts"
              data:
                q: request.term
              success: (matches) ->
                matches = JSON.parse(matches)
                results =
                  { label: name, value: name } for name in matches

                response(results)

            @

        remove_share: ( event ) =>
            user_row = $( event.currentTarget ).parent().parent()
            user = user_row.data( 'user' )

            $.ajax(
                type: "DELETE"
                url: "/repo/user_share/#{@repo.id}/?username=#{user}"
                data: "username=#{user}"
                success: () ->
                    user_row.remove() )
            @

        toggle_public: ( event ) =>
            $.post( "/repo/share/#{@repo.id}/", {}, ( response ) =>
                if response.success
                    $( event.currentTarget ).attr( 'checked', response.public )

                    if response.public
                        $( '#privacy > div' ).html( '<i class=\'fa fa-unlock\'></i>' )
                    else
                        $( '#privacy > div' ).html( '<i class=\'fa fa-lock\'></i>' )
            )
            @

        toggle_form_public: ( event ) =>
            $.post( "/repo/form_share/#{@repo.id}/", {}, ( response ) =>
                if response.success
                    $( event.currentTarget ).attr( 'checked', response.public )
            )
            @

    return ShareSettingsModal
)
