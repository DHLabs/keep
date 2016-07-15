define( [ 'jquery',
          'underscore',
          'backbone'
          'marionette',

          'app/collections/views/table' ],

( $, _, Backbone, Marionette, DataTableView) ->

    # Manages the data table and filter controls
    class DataFiltersView extends Backbone.Marionette.LayoutView
        el: '#filters-viz'

        template: '#filters-layout-tmpl'

        regions:
          'filter_controls': '.Filters-filterControls'
          'applied_filters': '.Filters-appliedFilters'
          'saved_filters':   '.Filters-savedFilters'
          'filtered_data':   '.Filters-filteredData'

        initialize: (options) -> @options = options

        onShow: ->
          # Setup view for filtered data
          @le_filtered_data = new FilteredDataView(@options)

          # Setup view for saved filters
          le_saved_filters = document.saved_filters
          @saved_filtersets = new FilterSets(le_saved_filters, parse: true)
          @saved_filters_view = new SavedFiltersView(collection: @saved_filtersets)

          # Setup view for currently applied filters,
          @current_filter_set = new FilterSet()
          @current_filters_view = new AppliedFiltersView(collection: @current_filter_set)

          # Filter controls need a list of possible column names to filter on
          column_names = _.map(@options.fields, (field) -> field.name)
          @filter_input = new FilterControls(columns: column_names)

          # Setup listening events
          @listenTo(@current_filters_view, 'filters:refresh_data', @_refresh_data)
          @listenTo(@current_filters_view, 'filters:save', @_save_filterset)
          @listenTo(@filter_input, 'filters:create', @_add_filter)
          @listenTo(@filter_input, 'filters:reset', @_reset_filterset)
          @listenTo(@saved_filters_view, 'filters:apply', @_apply_filterset)

          @filtered_data.show @le_filtered_data
          @filter_controls.show @filter_input
          @saved_filters.show @saved_filters_view
          @applied_filters.show @current_filters_view

          # Load up the intial set of data to render.
          @_refresh_data('')

        # Clear the currently applied filters and create a blank FilterSet
        _reset_filterset: -> @_apply_filterset new FilterSet()

        _apply_filterset: (filterset) ->
          @current_filter_set = filterset

          # Stop listening to old view, listen to new one
          @stopListening(@current_filters_view)
          @current_filters_view = new AppliedFiltersView(collection: @current_filter_set)
          @listenTo(@current_filters_view, 'filters:refresh_data', @_refresh_data)
          @listenTo(@current_filters_view, 'filters:save', @_save_filterset)

          @applied_filters.show @current_filters_view
          @_refresh_data()

        _save_filterset: (filterset) ->
          # Add or update filterset in saved filters collection
          if filterset.isNew() # add to saved collection
            @saved_filtersets.add(filterset)
          else # update existing one
            fs = @saved_filtersets.get(filterset.get('id'))
            fs.set(filterset.attributes)
            @saved_filters_view.render()
          filterset.save()

        # Add new filter to the current filter set (we modify the view's set
        # since it uses a copy, not the actual one) and refresh the data.
        _add_filter: (new_filter) ->
          @current_filters_view.collection.add(new_filter)
          @_refresh_data()

        _refresh_data: (url) ->
          # 1. update table data
          # 2. update CSV download link
          url or= @current_filters_view.collection.url_params()
          @le_filtered_data.filter_data(url)
          @$('.js-download').attr('href', @le_filtered_data.url + '&format=csv')


    class FilterControls extends Backbone.Marionette.ItemView
        template: '#filter-controls-tmpl'

        events:
            'click .js-add': 'create_filter'
            'click .js-reset': 'reset'

        # User wants to "unapply" a saved filter set or create a new one.
        reset: ->
          @trigger('filters:reset')

        # Create a new filter
        create_filter: (event) ->
          params =
            column_name: ($ '.columnName').val()
            filter_type: ($ '.filterType').val()
            filter_value: ($ '.filterValue').val()

          new_filter = new Filter(params)

          if not new_filter.isValid()
            # TODO: display validation error to user
            return @

          @$('.filterValue').val('')
          @trigger('filters:create', new_filter)

        # Fill the dropdown with a list of possible columns to filter on
        set_columns: (columns) ->
            les_options = _.map(columns, (column_name) ->
              "<option value='#{column_name}'>#{column_name}</option>"
            )
            @$('.columnName').html(les_options.join(''))

        onRender: ->
          @set_columns @options.columns

    # Table that holds the filtered data
    class FilteredDataView extends DataTableView

        initialize: (options) ->
          super options
          @base_url = @collection.url
          @on 'filters:refresh_data', @filter_data, @

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

        parse: (response) ->
          filter_type = /data__([\d|\w]+)__(gt|gte|lt|lte)/
          value_regex = /\=([\d|\w]*)/

          str = response

          # Check type of filter (ie. greater/less than)
          unless _.isEmpty(str.match filter_type)
            # e.g. splits "data__age__gt"
            [__, c_name, f_type]  = str.match(filter_type)[0].split('__')
          else
            f_type = 'eq'
            c_name = str.match(/data__([\d|\w]*)/)[0].split('__')[1]

          f_value = str.match(value_regex)[0].slice(1)

          {column_name: c_name, filter_type: f_type, filter_value: f_value}


        validate: (attrs) ->
            errors = []

            if attrs['filter_value'] is ''
              errors.push "Error: Filter value cannot be blank!"

            unless _.isEmpty(errors)
                for error in errors
                    console.log(error)
                return errors


    # Filters represents a collection of Filters, but is persisted on the
    # server as flat string (rather than a collection).
    class Filters extends Backbone.Collection
        model: Filter

        url: ->
          return "/api/v1/filters/?repo=#{@options.repo_id}"

        # Flattens filters collection into querystring params
        url_params: ->
          query_string = "?"
          for f in @models
            query_string += "&data__#{f.get 'column_name'}"
            query_string +=  "=" if f.get('filter_type') is 'eq'
            query_string +=  "__#{f.get 'filter_type'}=" if f.get('filter_type') isnt 'eq'
            query_string += "#{f.get 'filter_value'}"
          return query_string


    class FilterSet extends Backbone.Model
        defaults:
          user: ''
          repo: ''
          name: ''
          querystring: ''

        urlRoot: '/api/v1/filters/'

        toJSON: ->
          results =
            user: "" + @get('user')
            repo: "" + @get('repo')
            name: "" + @get('name')
            querystring: "" + @get('filters').url_params()
          results.id = "" + @get('id') if @get('id')
          results

        # The server returns a flattened querystring which we need to hydrate
        # into Backbone Models.
        parse: (response) ->
          filter_regex = /data__([\d|\w]*)=([\d|\w]*)/g

          matches = response.querystring.match(filter_regex)

          if not _.isEmpty(matches)
            response['filters'] = new Filters(matches, parse: true)

          response

        initialize: ->
          @set('user', "#{document.resource_ids.user_id}")
          @set('repo', "#{document.resource_ids.repo_id}")
          @set('filters', new Filters([]) ) if not @get('filters')

    class FilterSets extends Backbone.Collection
      model: FilterSet

    class AppliedFilterView extends Backbone.Marionette.ItemView
        template: '#filter-template'

        remove_filter: ->
          @trigger('filters:remove', @model)

        events:
          'click .js-remove': 'remove_filter'

        initialize: ->
          @listenTo(@model, 'destroy', @remove_filter)

    class EmptyAppliedFilters extends Backbone.Marionette.ItemView
      template: '#empty-filterset-tmpl'

    class AppliedFiltersView extends Backbone.Marionette.CompositeView
        template: '#filter-set-tmpl'
        emptyView: EmptyAppliedFilters
        childView: AppliedFilterView
        childViewContainer: '.activeFilters'

        events:
          'click .js-save': 'save_filterset'

        childEvents:
          'filters:remove': 'remove_filter'

        # We pass a FilterSet in, but actually iterate over a Filters
        # collection, which is hydrated from the flattened querystring saved on
        # a FilterSet.
        initialize: ->
          @filter_set = arguments[0].collection
          @collection = @filter_set.get('filters').clone()

        # First two parameters aren't important but passed along automatically
        # to functions called by childEvents.
        remove_filter: (__, ___, filter_model) ->
          @collection.remove(filter_model)
          @trigger('filters:refresh_data', @collection.url_params())

        onRender: ->
          @$('.Filters-fsNameField').val(@filter_set.get('name'))

        # Save/Patch the currently applied filterset
        save_filterset: ->
          # TODO: validate
          @filter_set.set('name', @$('.Filters-fsNameField').val())
          @filter_set.set('filters', @collection)
          @trigger('filters:save', @filter_set)

        serializeData: ->
          return { filterset_id: @filter_set.get('id') }

        templateHelpers:
          persist_label: ->
            return "Update" if @filterset_id
            return "Save"

    # Represents a filter set in the saved filter sets list
    class SavedFilterView extends Backbone.Marionette.ItemView
      template: '#saved-filter-tmpl'

      events:
        'click .js-apply': '_apply_filter'
        'click .js-delete': '_delete_filter'

      _apply_filter: (event) ->
        # TODO: visually indicate filter set is applied
        @trigger('filters:apply', @model)

      _delete_filter: ->
        @trigger('filters:delete', @model)

    class EmptySavedFilters extends Backbone.Marionette.ItemView
      template: '#empty-saved-filters-tmpl'

    # Represents the list of saved filters
    class SavedFiltersView extends Backbone.Marionette.CompositeView
      template: '#saved-filters-tmpl'
      emptyView: EmptySavedFilters
      childView: SavedFilterView
      childViewContainer: '.Filters-savedFilters'

      childEvents:
        'filters:apply': '_apply_filter'
        'filters:delete': '_delete_filter'

      _apply_filter: (__, filter_set) ->
        @trigger('filters:apply', filter_set)

      _delete_filter: (__, filter_set) ->
        @collection.remove(filter_set)
        filter_set.destroy()

    return DataFiltersView
)
