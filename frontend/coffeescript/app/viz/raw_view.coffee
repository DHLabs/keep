define( [ 'jquery',
          'underscore',
          'backbone'
          'marionette',

          'app/collections/views/table' ],

( $, _, Backbone, Marionette, DataTableView) ->


    class DataRawView extends DataTableView

        el: '#raw-viz'

        events:
          'click .js-sort': 'sort_table'

        sort_table: ->
          console.log 'sort table event fired'
          column = $(event.target)

          field = column.data 'field'
          sort_order = column.data('order') or 'none'

          sort_icon = $('i', column)

          # Set the new sort order.
          # Sort order changes from None -> Descending -> Ascending
          if sort_order is 'none'
            sort_order = 'desc'
            sort_icon.removeClass('icon-sort icon-sort-up').addClass('icon-sort-down')
          else if sort_order is 'desc'
            sort_order = 'asc'
            sort_icon.removeClass('icon-sort-down').addClass('icon-sort-up')
          else if sort_order is 'asc'
            sort_order = null
            sort_icon.removeClass('icon-sort-up').addClass('icon-sort')

          column.data('order', sort_order )

          @collection.sort_fetch( field: field, order: sort_order )


        # Handles hiding/showing fixed header
        detect_scroll: (event) ->

          return if @$el.is ':hidden'

          header_row   = @$('.DataTable-table thead')
          fixed_header = @$('.DataTable-fixedHeader')

          # Copy the header row of the table into the fixed header
          @$('.DataTable-fixedHead thead')
            .empty()
            .append header_row.html()

          # If we've scrolled past the header row of the table, make our
          # fixed header visible
          scrollTop  = $(event.currentTarget).scrollTop()
          offsetTop  = @$el.position().top

          if scrollTop > offsetTop then fixed_header.show() else fixed_header.hide()

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
