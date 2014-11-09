define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'app/models/data',
          'app/models/repo',

          'app/collections/repo',

          'app/viz/modals/sharing',
          'app/viz/raw_view',
          'app/viz/map_view',
          'app/viz/chart_view' ]

( $, _, Backbone, Marionette, DataModel, RepoModel, RepoCollection, ShareSettingsModal, DataRawView, DataMapView, DataChartView ) ->

    class DataSettingsView extends Backbone.Marionette.View
        el: '#settings-viz'

    class VizActions extends Backbone.Marionette.View
        # VizActions handles all page-wide actions that would result in a
        # modal being shown.
        #
        # In this case, there is only one action the sharing settings modal.
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

    class VizContainer extends Backbone.Marionette.Region
        el: '#viz-container'

        initialize: (options) ->
            # Initialize the different available views.
            @rawView = new DataRawView(options)
            @mapView = new DataMapView(options)
            @chartView = new DataChartView(options)
            @settingsView = new DataSettingsView(options)

            @views =
                raw: @rawView
                map: @mapView
                line: @chartView
                settings: @settingsView
            @attachView( @rawView )

            @currentView.render()
            if @currentView.showView? then @currentView.showView()
            if @currentView.onShow? then @currentView.onShow()


        switch_view: ( view ) ->
            # Hide the currently selected view
            if @currentView.hideView? then @currentView.hideView() else @currentView.$el.hide()

            # Attach the new view and render it
            @attachView( @views[ view ] )
            if @currentView.showView? then @currentView.showView() else @currentView.$el.show()

            # Call the onShow handler if it exists in the view
            if @currentView.onShow? then @currentView.onShow()

            @



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
        vizChrome    = new VizChrome( options )
        vizContainer = new VizContainer(options)

        DataVizApp.addRegions(chrome: vizChrome, viz: vizContainer)

        # Handle application wide events
        vizChrome.currentView.on( 'switch:raw', () ->
            vizContainer.switch_view( 'raw' ) )

        vizChrome.currentView.on( 'switch:map', () ->
            vizContainer.switch_view( 'map' ) )

        vizChrome.currentView.on( 'switch:line', () ->
            vizContainer.switch_view( 'line' ) )

        vizChrome.currentView.on( 'switch:settings', () ->
            vizContainer.switch_view( 'settings' ) )

        @

    return DataVizApp
)
