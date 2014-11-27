define( [ 'jquery',
          'underscore',
          'backbone'
          'marionette',

          'app/collections/views/table' ],

( $, _, Backbone, Marionette, DataTableView) ->



    class DataRawView extends DataTableView

        el: '#raw-viz .DataTable'

        detect_scroll: ( event ) ->

            return if @$el.is ':hidden'

            scrollTop  = $( event.currentTarget ).scrollTop()
            scrollLeft = $( event.currentTarget ).scrollLeft()

            offsetTop = @$el.position().top

            # Copy the header row of the table into the scroller div.
            header     = $('#fixed-header')
            header_row = $('tr:first-child', @el)
            $('table tr', header)
              .empty()
              .append header_row.html()
            header.css( 'width', header_row.width() )

            # Make sure our sorting still works
            @detect_sort(
                    fixed_el: header
                    el: @el
                    collection: @collection )

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

            return if @$el.is ':hidden'

            view_height = @$el.height()
            scroll_height = $( event.currentTarget ).scrollTop() + $( event.currentTarget ).height()

            if scroll_height + 100 > view_height
                @page_loading = true
                @collection.next( success: => @page_loading = false )

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

            # Unbind any existing events
            headers.unbind( 'click' )
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

        onShow: ->
            $( '#fixed-header' ).show()

        showView: ->
            ($ '#raw-viz').show()

        hideView: ->
            ($ '#raw-viz').hide()



        initialize: () ->
            DataTableView::initialize.apply(@, arguments)

            # Bind events to handle fixed-header rendering, sorting, and pagination
            # FIXME: scroll events should be bound to $el, not parent container
            $('#vizContainer').scroll( { view: @ }, (event) => @detect_scroll(event) )
            $('#vizContainer').scroll( { view: @ }, (event) => @detect_pagination(event) )
            @.on( 'render', @detect_sort )

            # Set the location of the data div and change it when we resize
            # the window.
            $( @el ).css( 'top', $( '#viz-chrome' ).height() + 1 + 'px' )
            $( window ).resize( ( event ) =>
                $( @el ).css( 'top', $( '#viz-chrome' ).height() + 1 + 'px' )
            )


            # Load up the intial set of data to render.
            @collection.reset( document.initial_data )

    return DataRawView
)
