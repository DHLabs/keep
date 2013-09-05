define( [ 'jquery',
          'underscore',
          'backbone'
          'marionette',

          'app/collections/views/data',
          'app/viz/map_view',
          'app/viz/chart_view' ],

( $, _, Backbone, Marionette, DataCollectionView, DataMapView, DataChartView ) ->


    class DataSettingsView extends Backbone.Marionette.View
        el: '#settings-viz'


    class DataRawView extends Backbone.Marionette.Region
        el: '#viz-data'

        detect_scroll: ( event ) ->

            if $( '#raw_table' ).is( ':hidden' )
                return

            scrollTop = $( event.currentTarget ).scrollTop()
            scrollLeft = $( event.currentTarget ).scrollLeft()

            offsetTop = $( '#raw_table' ).position().top

            # Copy the header row of the table into the scroller div.
            header = $( '#fixed-header' )
            header_row = $( '#raw_table tr:first-child' )
            $( 'table tr', header ).empty().append( header_row.html() )
            header.css( 'width', header_row.width() )

            # TODO
            # Handle click events on the fixed header so that we trigger a
            # sort.

            # If we've scrolled past the header row of the table, make our
            # fixed header visible
            if scrollTop > offsetTop
                header.css( { left: "-#{scrollLeft}px" } ).show()
            else
                # Otherwise just hide the sucker.
                header.hide()
            @

        detect_sort: ( options ) ->

            if options.el?
                headers = $( 'th', options.el )
            else
                headers = $( 'th', @el )

            headers.click( (event) =>
                el = $( event.currentTarget )

                field = el.data( 'field' )
                order = el.data( 'order' )

                # Permutate through the ordering options for the sort.
                if not order?
                    order = 'desc'
                    $( 'i', el ).removeClass( 'icon-sort icon-sort-up' ).addClass( 'icon-sort-down' )
                else if order == 'desc'
                    order = 'asc'
                    $( 'i', el ).removeClass( 'icon-sort-down' ).addClass( 'icon-sort-up' )
                else if order == 'asc'
                    order = null
                    $( 'i', el ).removeClass( 'icon-sort-up' ).addClass( 'icon-sort' )

                el.data( 'order', order )
                @collection.sort(
                    field: field
                    order: order )
            )
            @

        switch_view: ( view ) ->
            # Hide the currently selected view
            @currentView.$el.hide()

            # Attach the new view and render it
            @attachView( @views[ view ] )
            @currentView.$el.show()

            # Call the onShow handler if it exists in the view
            if @currentView.onShow? then @currentView.onShow()

            @

        initialize: ( options ) ->
            # Bind scroll event to handle the fixed-header rendering.
            $( @el ).scroll( @detect_scroll )

            # Initialize the different available views.
            @rawView = new DataCollectionView( options )
            @mapView = new DataMapView( options )
            @chartView = new DataChartView( options )
            @settingsView = new DataSettingsView( options )

            @views =
                raw: @rawView
                map: @mapView
                line: @chartView
                settings: @settingsView
            @attachView( @rawView )

            # Attach events where necessary.
            @rawView.on( 'render', @detect_sort )

            # Load up the intial set of data to render.
            @rawView.collection.reset( document.initial_data )

    return DataRawView
)