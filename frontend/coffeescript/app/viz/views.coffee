define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'app/models/data',
          'app/models/repo',

          'app/collections/repo',

          'app/viz/modals/sharing',
          'app/viz/raw_view',

          'backbone_modal',
          'jqueryui' ],

( $, _, Backbone, Marionette, DataModel, RepoModel, RepoCollection, ShareSettingsModal, DataRawView ) ->


    class VizActions extends Backbone.Marionette.View
        # VizActions handles all page-wide actions that would result in a
        # modal being shown.
        #
        # In this case, there is only one action the sharing settings modal.
        el: '#viz-actions'

        events:
            'click #share-btn': 'sharing_settings'
            'click #add_patient': 'add_patient'
            'click #go_to_list': 'go_to_list'
            'click #return_to_home': 'return_to_home'

        initialize: ( options ) ->
            @options = options

        go_to_list: (event) ->
            window.location = '/' + document.repo_owner + '/patient_list/' + window.location.search

        return_to_home: (event) ->
            window.location = 'http://www.0by25.org/accounts/login'

        add_patient: (event) ->
            window.location = '/' + document.repo_owner + '/' + document.repo.name + '/webform/' + window.location.search

        sharing_settings: ( event ) ->
            @modalView = new ShareSettingsModal( @options )
            $('.modal').html( @modalView.render().el )
            @modalView.onAfterRender( $( '.modal' ) )


    class VizTabs extends Backbone.Marionette.View
        el: '#viz-options'

        events:
            'click li': 'switch_event'

        switch_event: ( event ) ->
            target = $( event.currentTarget )

            if @selected().attr( 'id' ) == target.attr( 'id' )
                return

            if target.hasClass( 'disabled' )
                return

            @selected().removeClass( 'active' )
            target.addClass( 'active' )

            @trigger( 'switch:' + target.data( 'type' ) )

        selected: () ->
            # Return the currently selected tab
            return $( 'li.active', @el )


    class VizChrome extends Backbone.Marionette.Region
        el: '#viz-chrome'

        initialize: ( options ) ->
            @vizActions = new VizActions( options )
            @vizTabs = new VizTabs( options )

            @attachView( @vizTabs )


    # Instantiate and startup the new process.
    DataVizApp = new Backbone.Marionette.Application

    DataVizApp.addInitializer ( options ) ->

        @repo = new RepoModel( document.repo )
        @linked = new RepoCollection( document.linked_repos )

        options =
            repo: @repo
            linked: @linked
            fields: @repo.fields()
            visualizations: document.visualizations

        # Add the different regions
        vizChrome = new VizChrome( options )
        rawView   = new DataRawView( options )

        DataVizApp.addRegions(
                chrome: vizChrome
                viz: rawView )

        # Handle application wide events
        vizChrome.currentView.on( 'switch:raw', () ->
            rawView.switch_view( 'raw' ) )

        vizChrome.currentView.on( 'switch:map', () ->
            rawView.switch_view( 'map' ) )

        vizChrome.currentView.on( 'switch:line', () ->
            rawView.switch_view( 'line' ) )

        vizChrome.currentView.on( 'switch:settings', () ->
            rawView.switch_view( 'settings' ) )

        @

    return DataVizApp
)