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

            currentView = event.data.view.currentView

            if $( currentView.el ).is( ':hidden' )
                return

            scrollTop = $( event.currentTarget ).scrollTop()
            scrollLeft = $( event.currentTarget ).scrollLeft()

            offsetTop = $( currentView.el ).position().top

            # Copy the header row of the table into the scroller div.
            header = $( '#fixed-header' )
            header_row = $( 'tr:first-child', currentView.el )
            $( 'table tr', header ).empty().append( header_row.html() )
            header.css( 'width', header_row.width() )

            # Make sure our sorting still works
            event.data.view.detect_sort(
                    fixed_el: header
                    el: event.data.view.currentView.el
                    collection: event.data.view.currentView.collection )

            # If we've scrolled past the header row of the table, make our
            # fixed header visible
            if scrollTop > offsetTop
                header.css( { left: "-#{scrollLeft}px" } ).show()
            else
                # Otherwise just hide the sucker.
                header.hide()

            @

        detect_pagination: ( event ) ->

            # Don't load another page while the page is being requested from the
            # server
            if @page_loading? and @page_loading
                return

            currentView = event.data.view.currentView

            if $( currentView.el ).is( ':hidden' )
                return

            view_height = currentView.$el.height()
            scroll_height = $( event.currentTarget ).scrollTop() + $( event.currentTarget ).height()

            if scroll_height + 100 > view_height
                @page_loading = true
                currentView.collection.next( success: ()=>
                    @page_loading = false )

            @

        detect_sort: ( options ) ->

            event_data = {}

            if options.el?
                headers = $( 'th', options.fixed_el )

                event_data =
                    collection: options.collection
                    headers: $( 'th', options.el )
            else
                headers = $( 'th', @el )

                event_data =
                    collection: @collection

            headers.click( event_data, (event) ->

                el = $( event.currentTarget )

                field = el.data( 'field' )
                order = el.data( 'order' )

                # Update both the fixed and real table header if the click was
                # detected on the fixed header. Since the fixed header is a
                # completely separate table, we have to do a little jQuery magic
                # to select both tables.
                if event.data.headers?
                    other_el = $( event.data.headers ).filter( ()->
                                return $( @ ).data( 'field' ) == field )

                # Create the selector that includes both the real & fixed header
                # table header.
                if other_el?
                    els = $().add( 'i', el ).add( 'i', other_el )
                else
                    els = $( 'i', el )

                # Permutate through the ordering options for the sort.
                if not order?
                    order = 'desc'
                    els.removeClass( 'icon-sort icon-sort-up' ).addClass( 'icon-sort-down' )

                else if order == 'desc'
                    order = 'asc'
                    els.removeClass( 'icon-sort-down' ).addClass( 'icon-sort-up' )

                else if order == 'asc'
                    order = null
                    els.removeClass( 'icon-sort-up' ).addClass( 'icon-sort' )

                # Update the order for both the real & fixed table
                el.data( 'order', order )
                other_el.data( 'order', order ) if other_el?

                # Sort the sucker! The view should automatically refresh when
                # the sort results are finally received.
                event.data.collection.sort_fetch(
                                field: field
                                order: order )
            )
            @

        switch_view: ( view ) ->
            $( '#fixed-header' ).hide()

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
            $( @el ).scroll( { view: @ }, @detect_scroll )
            # Bind scroll event to handle pagination ( scrolling to the end of the
            # page. )
            $( @el ).scroll( { view: @ }, @detect_pagination )

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