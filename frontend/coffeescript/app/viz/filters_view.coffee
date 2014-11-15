define( [ 'jquery',
          'underscore',
          'backbone'
          'marionette',

          'app/collections/views/table' ],

( $, _, Backbone, Marionette, DataTableView) ->

    class DataFiltersView extends DataTableView

        el: '#filters-viz .DataTable'

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
            ($ '.fixed-header' ).show()

        showView: ->
            ($ '#filters-viz').show()

        hideView: ->
            ($ '#filters-viz').hide()

        # Refresh table data according to filters
        _refresh_data: (url_params) ->
            # 1. change data table's url
            # 2. reset table view
            # 3. update CSV download link
            @collection.url = @base_url + url_params
            ($ '#filters-viz .js-download').attr('href', @collection.url + '&format=csv')
            @collection.fetch(reset: true)

        _setup_filters: ->
            saved_filters = []
            @filters_collection = new FilterCollection(saved_filters)
            @filter_views = new FiltersView(collection: @filters_collection)
            @filter_views.render()


            # FIXME: filter views should be able to render at initialization
            # using a templateHelper method but I can't figure out how to
            # bind an instance variable (the set of column names) in the right scope
            @filter_views.set_columns(@column_names)

            # Listen to filters collection for changes
            @listenTo(@filter_views, 'filters:refresh_data', @_refresh_data)



        initialize: () ->
            DataTableView::initialize.apply(@, arguments)

            # Bind scroll event to handle the fixed-header rendering, and
            # lazy-loading of data
            @$el.scroll( { view: @ }, @detect_scroll )
            @$el.scroll( { view: @ }, @detect_pagination )

            # Set the location of the data div and change it when we resize
            # the window.
            @$el.css('top', $( '#viz-chrome' ).height() + 1 + 'px')
            $(window).resize( ( event ) =>
                @$el.css( 'top', $( '#viz-chrome' ).height() + 1 + 'px' )
            )

            @on('render', @detect_sort)

            # Need to pass column names along to FiltersView for dropdown
            @column_names = _.map(@fields, (field) -> field.label)

            # Save base url to use with filtering
            @base_url = @collection.url

            # Set up controls to manage filters
            @_setup_filters()

            # Load up the intial set of data to render.
            @_refresh_data(@filter_views.collection.url_params())


    class Filter extends Backbone.Model
        defaults:
            column_name: ''
            filter_type: ''
            filter_value: ''

        validate: (attrs) ->
            errors = []

            for attr in attrs
                if attrs == ''
                    errors.append "Error: #{attr} cannot be blank!"

            unless _.isEmpty(errors)
                for error in errors
                    console.log(error)
                return errors


    class FilterCollection extends Backbone.Collection
        model: Filter

        # Flattens filters collection into querystring params
        url_params: ->
            query_string = "?"
            for f in @models
              query_string += "&data__#{f.get 'column_name'}=#{f.get 'filter_value'}"
            return query_string

        render: ->
          Backbone.Collection::render.apply(@, arguments)


    class FilterView extends Backbone.Marionette.ItemView
        template: '#filter-template'

        remove_filter: ->
            @trigger('filters:remove', @model)

        events:
          'click .js-remove': 'remove_filter'

        initialize: ->
            @listenTo(@model, 'destroy', @remove_filter)


    class FiltersView extends Backbone.Marionette.CompositeView
        el: '#filterControls'
        template: '#filter-controls'
        itemView: FilterView
        itemViewContainer: '.activeFilters'

        add_filter: (event) ->
            params =
                column_name: ($ '.columnName').val()
                filter_type: ($ '.filterType').val()
                filter_value: ($ '.filterValue').val()

            new_filter = new Filter(params)
            # TODO: verify inputs are valid
            # TODO: clear inputs on success
            @collection.add(new_filter)
            @trigger('filters:refresh_data', @collection.url_params())

        remove_filter: (event) ->
            @collection.remove(event.model)
            @trigger('filters:refresh_data', @collection.url_params())

        events:
            'click .js-add': 'add_filter'

        set_columns: (columns) ->
            les_options = _.map(columns, (column_name) ->
              "<option value='#{column_name}'>#{column_name}</option>"
            )
            $('.columnName').html(les_options.join(''))

        initialize: (options) ->
            Backbone.Marionette.CollectionView::initialize.apply(@, arguments)

            @on('itemview:filters:remove', @remove_filter)


    return DataFiltersView
)
