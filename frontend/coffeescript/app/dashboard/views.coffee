define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          # Model stuff
          'app/collections/views/repo',
          'app/collections/views/study',
          'app/models/repo',

          # Modals/views
          'app/dashboard/modals/new_repo',
          'app/dashboard/modals/new_study',
          'app/dashboard/modals/study_settings',

          # Plugins, etc.
          'backbone_modal',
          'jqueryui',
          'jquery_cookie' ],

( $, _, Backbone, Marionette, RepoCollectionView, StudyCollectionView, RepoModel,
    NewRepoModal, NewStudyModal, StudySettingsModal ) ->

    class DashboardView extends Backbone.View
        el: $( '#dashboard' )

        filter: 'all'

        repo_list: $( '#repo_list > tbody' )
        study_list: $( '#study_list' )

        events:
            "click #studies .create-new a":     "new_study_event"
            "click .study-settings a":          "study_settings_event"

            "click #filters li a":              "filter_repos_event"
            "click #studies ul li a":           "refresh_repos_event"
            "click #repos #refresh-repos":      "refresh_repos_event"

        _apply_draggable: () =>
            # When the view is finished rendering or refreshed, add the
            # droppable event to each study in the study list.
            $( 'li', '#study_list' ).droppable(
                hoverClass: 'drop-hover'
                drop: @_drop_on_study )

            @

        _drop_on_study: ( event, ui ) =>
            # Grab the study & repo ids
            study_id = $( 'a', event.target ).data( 'study' )
            study_id = null if not study_id?

            repo = new RepoModel()
            repo_id = $( ui.draggable ).data( 'repo' )
            repo.save( { id: repo_id, study: study_id },
                    patch: true
                    success: ( response, textStatus, jqXhr ) =>
                        if @study_view.selected()? and @study_view.selected() != study_id
                            @repo_view.collection.remove( {id: repo_id} )
            )

            @

        file_dragleave: ( event ) ->

            @drag_overlay_timer = setTimeout( ()->
                event.stopPropagation()
                $( '#file-drop-overlay' ).hide()
            , 300 )

            @

        file_dragover: ( event ) ->

            clearTimeout( @drag_overlay_timer )
            event.stopPropagation()
            event.preventDefault()
            $( '#file-drop-overlay' ).show();

            @

        file_drop: ( event ) =>

            if not event.originalEvent.dataTransfer?
                return

            event.stopPropagation()
            event.preventDefault()

            # Pass in the options needed for the modal
            options =
                # The files dragged into the window
                files: event.originalEvent.dataTransfer.files
                # The studies the user has, if they want to include this
                # file as a new repo in this study.
                studies: @study_view.collection
                # Callback when the file is successfully uploaded
                success: ( data ) ->

                    if data.success
                        $( '#refresh-repos' ).trigger( 'click' )
                    else
                        console. log( data )
                # Callback if we receive an error of some sort.
                error: ( data ) ->
                    # TODO: Gracefully handle upload error
                    console.log( data )

            @modalView = new NewRepoModal( options )
            $( '.modal' ).html( @modalView.render().el )
            $( '#file-drop-overlay' ).hide()

            @

        filter_repos_event: (event) ->
            $( '.selected', '#filters' ).removeClass( 'selected' )
            $( event.currentTarget ).parent().addClass( 'selected' )

            @repo_view.filter( $( event.currentTarget ).data( 'filter' ) )

        new_study_event: (event) ->
            @modalView = new NewStudyModal( { collection: @study_view.collection } )
            $('.modal').html( @modalView.render().el )
            $( '#study-name' ).focus()

        study_settings_event: (event) ->
            event.stopImmediatePropagation()

            # Grab the study that this is for.
            study = @study_view.collection.findWhere( { id: $( event.currentTarget ).data( 'study' ) })
            options =
                study: study
                collection: @study_view.collection
                tracker: @repo_view.collection.where( { study: study.get( 'name' ) } )

            # Create the modal and display it!
            @modalView = new StudySettingsModal( options )
            $('.modal').html( @modalView.render().el )

        initialize: ->
            # Initialize our collections!
            @repo_view = new RepoCollectionView
            @repo_view.collection.reset( document.repo_list )

            @study_view = new StudyCollectionView
            @study_view.on( 'render', @_apply_draggable )
            @study_view.collection.reset( document.study_list )

            @study_view.on( 'after:item:added', @refresh_repos_event )
            @study_view.on( 'item:removed', @refresh_repos_event )

            # TODO: Detect ability to read local files in the browser. This
            # is a notably HTML5 feature and should be in most if not all browsers
            # but you never know...
            $(window).bind( 'dragover', @file_dragover )
            $(window).bind( 'drop', @file_drop )
            $( '#file-drop-overlay' ).bind( 'dragleave', @file_dragleave )

            $( 'li', '#studies' ).droppable(
                hoverClass: 'drop-hover'
                drop: @_drop_on_study )
            @

        refresh_repos_event: ( event ) =>

            # Manual refresh of the currently selected study
            if event.currentTarget? and $( event.currentTarget ).attr( 'id' ) == 'refresh-repos'
                study_el   = $( '#studies .selected > a' )
                study_id   = $( study_el ).data( 'study' )
                study_name = $( study_el ).html()

            # A study was clicked, switch to that study and refresh the screen!
            else if event.currentTarget?
                study_el   = event.currentTarget
                study_id   = $( study_el ).data( 'study' )
                study_name = $( study_el ).html()

            # A repo/study was removed
            else
                study_el   = event.el
                study_id   = event.model.id
                study_name = event.model.get( 'name' )

                # Was this item removed or added? If isClosed is true, the item
                # was removed from the collection.
                if event.isClosed
                    study_id = null
                    study_name = 'All Diaries'

            # Update the "Study" name and highlight the one the user just clicked.
            $( '#study_name' ).html( study_name  )
            $( '#studies .selected' ).removeClass( 'selected' )
            $( study_el ).parent().addClass( 'selected' )

            # Fetch the new set of repositories
            @repo_view.refresh( study_id )

            @

    return DashboardView
)