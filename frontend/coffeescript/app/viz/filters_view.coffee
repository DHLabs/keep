define( [ 'jquery',
          'underscore',
          'backbone'
          'marionette',

          'app/collections/views/table' ],

( $, _, Backbone, Marionette, DataTableView) ->

    class DataFiltersView extends DataTableView

        el: '#filteredData'

        # Refresh table data according to filters
        _refresh_data: (url_params) ->
            # 1. change data table's url
            # 2. reset table view
            # 3. update CSV download link
            @collection.url = @base_url + url_params
            ($ '#filters-viz .js-download').attr('href', @collection.url + '&format=csv')
            @collection.fetch(reset: true)

        _setup_filters: ->
          # Save base url to use with filtering
          @base_url = @collection.url

          # TODO: allow filters to be saved
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

        initialize: (options) ->
          super options

          # Need to pass column names along to FiltersView for dropdown
          @column_names = _.map(@fields, (field) -> field.name)

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

        onRender: ->
          @on('itemview:filters:remove', @remove_filter)


    return DataFiltersView
)
