define( [ 'jquery',
          'underscore',
          'backbone',

          # Model stuff
          'app/collections/repo'
          'app/collections/study'
          'app/models/study'

          # Plugins, etc.
          'backbone_modal',
          'jqueryui',
          'jquery_cookie' ],

( $, _, Backbone, RepoCollection, StudyCollection, StudyModel ) ->

    class StudySettingsModal extends Backbone.Modal
        template: _.template( $( '#study-settings-template' ).html() )
        cancelEl: '.btn-primary'

        initialize: ( study )->
            @study = study

        delete_event: ( event ) =>
            @study.destroy()

        onRender: ()->
            $( '.study-name', @el ).html( @study.get( 'name' ) )
            $( '.study-delete', @el ).click( @delete_event )


    class NewStudyModal extends Backbone.Modal
        template: _.template( $( '#new-study-template' ).html() )
        submitEl: '.btn-primary'
        cancelEl: '.btn-cancel'

        clean: () ->
            values =
                name: $( '#study-name' ).val().replace( /^\s+|\s+$/g, "" )
                description: $( '#study-description' ).val().replace( /^\s+|\s+$/g, "" )
                tracker: $( '#study-tracker' ).is( ':checked' )

            return values

        beforeSubmit: () ->

            @cleaned_data = @clean()

            if @cleaned_data[ 'name' ].length == 0
                $( '.error', $( '#study-name' ).parent() ).html( 'Please used a valid study name' )
                return false

        submit: () ->
            study = new StudyModel()
            study.save( @cleaned_data, {headers: {'X-CSRFToken': $.cookie( 'csrftoken' )}} )


    class DashboardView extends Backbone.View
        el: $( '#dashboard' )

        filter: 'all'

        repos: new RepoCollection()
        studies: new StudyCollection()

        repo_list: $( '#repo_list > tbody' )
        study_list: $( '#study_list' )

        events:
            "click #studies .create-new a":     "new_study_event"
            "click .study-settings a":          "study_settings_event"

            "click #filters li a":              "filter_repos_event"
            "click #studies ul li a":           "refresh_repos_event"

        study_templ = _.template( '''
                <li>
                    <div class='study-settings'>
                        <a href='#' data-name='<%= name %>' data-id='<%= id %>'><i class='icon-cog'></i></a>
                    </div>
                    <a href='#' data-study='<%= id %>'><%= name %></a>
                </li>''' )

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

        filter_repos_event: (event) ->
            @filter = $( event.currentTarget ).data( 'filter' )
            @_apply_filters( event.currentTarget )

        new_study_event: (event) ->
            @modalView = new NewStudyModal()
            $('.modal').html( @modalView.render().el )
            $( '#study-name' ).focus()

        study_settings_event: (event) ->
            study =
                id: $( event.currentTarget ).data( 'id' )
                name: $( event.currentTarget ).data( 'name' )

            @modalView = new StudySettingsModal( new StudyModel( study ) )
            $('.modal').html( @modalView.render().el )
            event.stopImmediatePropagation()

        initialize: ->
            @listenTo( @repos, 'reset', @render )

            # Initialize our collections!
            @repos.reset( document.repo_list )
            @studies.reset( document.study_list )

            @render()

        refresh_repos_event: (event) ->
            # Fetch repositories for a given study.
            # If "All Diaries" is selected, fetch repositories

            study_id = $( event.currentTarget ).data( 'study' )

            fetch_options =
                success: @render
                reset: true

            fetch_options[ 'data' ] = { study: study_id } if study_id?

            @repos.fetch( fetch_options )

            $( '#study_name' ).html( $( event.currentTarget ).html()  )

            if study_id?
                $( '#study-settings' ).show()
            else
                $( '#study-settings' ).hide()

            $( '#studies .selected' ).removeClass( 'selected' )
            $( event.currentTarget ).parent().addClass( 'selected' )

            @

        render: =>

            for study in @studies.models
                study_el = study_templ( study.attributes )
                console.log( study )
                @study_list.append( study_el )

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