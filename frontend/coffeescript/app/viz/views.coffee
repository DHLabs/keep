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
        el: '#viz-actions'

        events:
            'click #share-btn': 'sharing_settings'

        initialize: ( options ) ->
            @options = options

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

        # Add the different regions
        vizChrome = new VizChrome( { repo: @repo } )
        rawView   = new DataRawView( { repo: @repo, linked: @linked, fields: @repo.fields() } )

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