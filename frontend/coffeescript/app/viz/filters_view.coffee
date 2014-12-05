define( [ 'jquery',
          'underscore',
          'backbone'
          'marionette',

          'app/collections/views/table' ],

( $, _, Backbone, Marionette, DataTableView) ->

    # Manages the data table and filter controls
    class DataFiltersView extends Backbone.Marionette.View
        el: '#filters-viz'

        initialize: (options) ->
          @filtered_data = new FilteredDataView(options)
          @filtered_data.render()

          # TODO: allow filters to be saved
          saved_filters = []
          @filters_collection = new FilterCollection(saved_filters)
          @filter_views = new FiltersView(collection: @filters_collection)

          # Set column names in dropdown
          @filter_views.render()
          @column_names = _.map(options.fields, (field) -> field.name)
          @filter_views.set_columns(@column_names)

          # Listen to filters collection for changes
          @listenTo(@filter_views, 'filters:refresh_data', @_refresh_data)

          # Load up the intial set of data to render.
          @_refresh_data('')

        _refresh_data: ->
          # 1. update table data
          # 2. update CSV download link
          @filtered_data.filter_data(@filters_collection.url_params())
          @$('.js-download').attr('href', @filtered_data.url + '&format=csv')


    # Table that holds the filtered data
    class FilteredDataView extends DataTableView
        el: '#filteredData'

        initialize: (options) ->
          super options
          @base_url = @collection.url

        url: ->
          return @collection.url

        # update table with filtered data
        filter_data: (url_params) ->
          # 1. change data table's url
          # 2. reset table view (calls server for new data)
          @collection.url = @base_url + url_params
          @collection.fetch(reset: true)


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
              query_string += "&data__#{f.get 'column_name'}"
              query_string +=  "=" if f.get 'filter_type' is 'eq'
              query_string +=  "__#{f.get 'filter_type'}=" if f.get('filter_type') isnt 'eq'
              query_string += "#{f.get 'filter_value'}"
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
