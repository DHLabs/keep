define( [ 'jquery',
          'underscore',
          'backbone',
          'jqueryui' ],

( $, _, Backbone ) ->

    class RepoCollection extends Backbone.Collection
        initialize: ->
            @url = '/api/v1/repos'

        parse: ( response ) ->
            return response.objects


    class DashboardView extends Backbone.View
        el: $( '#dashboard' )

        filter: 'all'

        repos: new RepoCollection()
        repo_list: $( '#repo_list > tbody' )

        events:
            "click #studies ul li a":   "refresh_event"
            "click #filters li a":      "filter_event"

        repo_tmpl  = _.template( '''
            <tr class="<%= filters %>" data-repo="<%= id %>">
                <td class='privacy'>
                    <%= privacy_icon %>
                </td>
                <td class='add-data'>
                    <a href='<%= webform_uri %>' class='btn btn-small'>
                        <i class='icon-pencil'></i> Add Data
                    </a>
                </td>
                <td>
                    <a href='<%= uri %>'>
                        <%= name %>
                        <div class='help-block'>
                            <%= description %>
                        </div>
                    </a>
                </td>
                <td class='submission-count'>
                    <%= submissions %>&nbsp;<i class='icon-file-alt'></i>
                </td>
            </tr>''' )

        _apply_filters: (target) ->

            if @filter == 'all'
                $( 'tr', @repo_list ).fadeIn( 'fast' )
            else
                filter = @filter
                $( 'tr', @repo_list ).each( ()->
                    if $( @ ).hasClass( filter )
                        $( @ ).fadeIn( 'fast' )
                    else
                        $( @ ).fadeOut( 'fast' )
                )

            # Only reset the selected filter if we've actually received a click
            # event, rather than a programmatic filter.
            if target?
                $( '#filters .selected' ).removeClass( 'selected' )
                $( target).parent().addClass( 'selected' )

        filter_event: (event) ->
            @filter = $( event.currentTarget ).data( 'filter' )
            @_apply_filters( event.currentTarget )

        initialize: ->
            @listenTo( @repos, 'reset', @render )

            @repos = new RepoCollection()
            @repos.reset( document.initial_data )

            @render()

        refresh_event: (event) ->
            # Fetch repositories for a given study.
            # If "All Diaries" is selected, fetch repositories

            study_id = $( event.currentTarget ).data( 'study' )

            fetch_options =
                success: @render
                reset: true

            fetch_options[ 'data' ] = { study: study_id } if study_id?

            @repos.fetch( fetch_options )

            $( '#study_name' ).html( $( event.currentTarget ).html()  )

            $( '#studies .selected' ).removeClass( 'selected' )
            $( event.currentTarget ).parent().addClass( 'selected' )

            @

        render: =>

            # Clear the repo table.
            $( @repo_list ).empty()

            for repo in @repos.models

                filters = []

                if repo.get( 'is_public' )
                    privacy_icon = '<icon class="icon-unlock"></i>'
                    filters.push( 'public' )
                else
                    privacy_icon = '<icon class="icon-lock"></i>'
                    filters.push( 'private' )

                if repo.get( 'org' )
                    filters.push( 'shared' )

                # Copy the repo metadata into a new object
                repo_attrs = $.extend( true, {}, repo.attributes )
                # Add the additional bits of metadata we need to do filters and
                # show off the fancy privacy icon
                repo_attrs[ 'filters' ] = filters.join( ' ' )
                repo_attrs[ 'privacy_icon' ] = privacy_icon

                # Create the repo HTML and add it to the DOM
                repo_el = repo_tmpl( repo_attrs )
                @repo_list.append( repo_el )

            # Apply draggable/droppable attributes to the new repo rows.
            $( "#repo_list tr" ).draggable(
                helper: 'clone'
                opacity: 0.7
            )

            $( "#studies li" ).droppable(
                hoverClass: 'drop-hover'
                drop: ( event, ui ) ->
                    study_id = $( 'a', @ ).data( 'study' )
                    if not study_id?
                        study_id = null

                    repo_id = $( ui.draggable ).data( 'repo' )

                    console.log( "Moving #{repo_id} to #{study_id}" )

                    $.ajax(
                        headers:
                            'Accept' : 'application/json'
                            'Content-Type' : 'application/json'
                        url: "/api/v1/repos/#{repo_id}"
                        type: 'PATCH',
                        data: JSON.stringify( { 'study': study_id } )
                        success: ( response, textStatus, jqXhr ) ->
                            console.log( response )
                    )
                )

            @_apply_filters()

            @

    return DashboardView
)