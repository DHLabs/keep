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
          'app/viz/chart_view',
          'app/viz/filters_view',
      ]

( $, _, Backbone, Marionette, DataModel, RepoModel, RepoCollection, ShareSettingsModal, DataRawView, DataMapView, DataChartView, DataFiltersView ) ->

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
            # Prevents URL from changing back to '#'
            event.preventDefault()

            target = $( event.currentTarget )

            if @selected().data('type') is target.data('type')
                return

            if target.hasClass( 'disabled' )
                return

            @selected().removeClass( 'active' )
            target.addClass( 'active' )

            @trigger( 'switch:' + target.data( 'type' ) )

        selected: ->
            # Return the currently selected tab
            return @$('li.active')

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
            @filtersView = new DataFiltersView(options)
            @settingsView = new DataSettingsView(options)

            @views =
                raw: @rawView
                map: @mapView
                line: @chartView
                filters: @filtersView
                settings: @settingsView

            # Attach and show initial view
            current_route = Backbone.history.getFragment()
            initial_view = @views[current_route]
            initial_view or= @rawView
            @show(initial_view)
            @currentView.$el.show()

            @

        switch_view: (view) ->
          @currentView.$el.hide()
          @show(@views[view], preventDestroy: true)
          @currentView.$el.show()
          Backbone.history.navigate(view)


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
        views = ['raw', 'map', 'line', 'filters', 'settings']
        _.each(views, (view) ->
          vizChrome.currentView.on( "switch:#{view}", -> vizContainer.switch_view view )
        )

        @

    return DataVizApp
)
