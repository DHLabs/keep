define( [ 'jquery',
          'underscore',
          'backbone'
          'marionette',
          'app/collections/views/data' ],

( $, _, Backbone, Marionette, DataCollectionView ) ->

   class DataRawView extends Backbone.Marionette.Region
        el: '#viz-data'

        detect_scroll: ( event ) ->

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
                    repo: @repo
                    field: field
                    order: order )
            )
            @

        initialize: ( options ) ->
            # Bind scroll event to handle the fixed-header rendering.
            $( @el ).scroll( @detect_scroll )

            # Initialize and create the DataCollectionView.
            @rawView = new DataCollectionView( options )
            @attachView( @rawView )

            # Attach events where necessary.
            @rawView.on( 'render', @detect_sort )

            # Load up the intial set of data to render.
            @rawView.collection.reset( document.initial_data )

    return DataRawView
)