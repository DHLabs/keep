define( [ 'jquery',
          'underscore',
          'backbone'
          'marionette',

          'app/collections/views/table' ],

( $, _, Backbone, Marionette, DataTableView) ->

    class DataFiltersView extends DataTableView

        el: '#filters-viz .DataTable'

        events:
          'click .js-sort': 'sort_table'

        sort_table: ->
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


        detect_pagination: (event) ->
          # Don't load another page while the page is being requested from the
          # server
          return if @page_loading

          return if @$el.is ':hidden'

          view_height = @$el.height()
          scroll_height = $( event.currentTarget ).scrollTop() + $( event.currentTarget ).height()

          if scroll_height + 100 > view_height
              @page_loading = true
              @collection.next( success: => @page_loading = false )

          @

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

            # Bind events to handle pagination
            $('#vizContainer').scroll( { view: @ }, (event) => @detect_pagination(event) )

            # Set the location of the data div and change it when we resize
            # the window.
            @$el.css('top', $( '#viz-chrome' ).height() + 1 + 'px')
            $(window).resize( ( event ) =>
                @$el.css( 'top', $( '#viz-chrome' ).height() + 1 + 'px' )
            )

            # Need to pass column names along to FiltersView for dropdown
            @column_names = _.map(@fields, (field) -> field.name)

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
