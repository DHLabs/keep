define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'app/collections/data',
          'app/viz/modals/data_details' ]

( $, _, Backbone, Marionette, DataCollection, DataDetailsModal ) ->

    class EmptyTableView extends Backbone.Marionette.ItemView
        tagName: 'tr'
        template: _.template '''
              <td>There is no data for this table!</td>
        '''

    class TableRowView extends Backbone.Marionette.ItemView
        tagName: 'tr'

        events:
            'click':    'clicked'

        data_templates:
            'text':     _.template( '<td><%= data %></td>' )
            'geopoint': _.template( '<td><%= data.coordinates[1] %>, <%= data.coordinates[0] %></td>' )
            'photo':    _.template( '<td><a href="<%= data %>" target="blank">Click to view photo</a></td>'  )

            'forms':    _.template '''
                    <td>
                    <% _.each(document.linked_repos, function(item) { %>
                        <% if( model.linked[item.name]) { %>
                            <span style="color:#00ff00"><%= item.name %></span>
                        <% } else { %>
                            <span style="color:#ff0000"><%= item.name %></span>
                        <% }; %>&nbsp;&nbsp;
                    <% }); %>
                    </td>
                '''
        initialize: (options) ->
            @fields = options.fields
            @repo   = options.repo
            @linked = options.linked

        template: ( model ) =>
            # Based on the field type, we use a specific formatter for that
            # data type.
            templ = []

            if @repo.attributes.is_tracker
                templ.push( @data_templates[ 'forms' ]( { model: model } ) )

                #callbacks to check if form is filled out for data
                @check_filled_forms( model )

            for field in @fields
                tdata = { data: model.data[ field.name ] }

                if field.type in [ 'geopoint', 'photo' ]
                    if tdata['data']
                        templ.push( @data_templates[ field.type ]( tdata ) )
                    else
                        templ.push( @data_templates[ 'text' ]( tdata ) )
                else
                    templ.push( @data_templates[ 'text' ]( tdata ) )

            # Fix for fixed-width tables. The last td is flexible, thus making
            # the tds before it fixed.
            templ.push( '<td>&nbsp;</td>' )
            return templ.join( '' )

        clicked: (event) =>

            if event.target == 'a'
                event.stopPropagation()

            options =
                repo: @repo
                model: @model
                linked: @linked
                fields: @fields

            modalView = new DataDetailsModal(options)
            ($ '.modal').html modalView.render().el
            modalView.onAfterRender($ '.modal')

            return true


    class DataTableView extends Backbone.Marionette.CompositeView
        itemView: TableRowView
        emptyView: EmptyTableView
        template: '#DataTable-template'

        itemViewContainer: '.DataTable-table tbody'

        header_template: _.template '''
                <tr>
                <% if(repo.attributes.is_tracker) { %>
                    <th>Linked Forms</th>
                <% }; %>
                <% _.each( fields, function( item ) { %>
                    <th class="js-sort" data-field='<%= item.name %>'>
                        <%= item.name %><i class='sort-me icon-sort'></i>
                    </th>
                <% }); %>
                    <th>&nbsp;</th>
                </tr>
            '''

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

        onRender: =>
          # Populate table headers
          @$('.DataTable-table thead').append @header_template(fields: @fields, repo: @repo)
          @$('.DataTable-fixedHeader thead').append @header_template(fields: @fields, repo: @repo)

          # Bind events to handle fixed-header rendering and pagination
          @$('.DataTable').scroll( { view: @ }, (event) => @detect_pagination(event) )
          @$('.DataTable').scroll( { view: @ }, (event) => @detect_scroll(event) )

        # Indicate loading by applying opacity to table
        show_loading: ->
          @$el.addClass('u-fade50')

        # Remove loading indicator (opacity)
        hide_loading: ->
          @$el.removeClass('u-fade50')


        initialize: (options)->

          @fields = options.fields
          @repo   = options.repo
          @linked = options.linked

          @collection = new DataCollection(options)

          # Setup loading indicators:
          # 1. apply opacity when request is fired
          # 2. remove opacity when collection synced
          @listenTo(@collection, 'request', @show_loading)
          @listenTo(@collection, 'sync', @hide_loading)

          @


        # Handles hiding/showing fixed header
        detect_scroll: (event) ->

          return if @$el.is ':hidden'

          header_row   = @$('.DataTable-table thead')
          fixed_header = @$('.DataTable-fixedHeader')

          # Copy the header row of the table into the fixed header
          @$('.DataTable-fixedHead thead')
            .empty()
            .append header_row.html()

          console.log 'detecting scroll event'

          # If we've scrolled at all in the table, make the fixed header visible
          scrollTop = @$('.DataTable').scrollTop()
          if scrollTop > 0
            fixed_header.show()
            fixed_header.css('position', 'fixed').css('top', @_calculate_dist_from_top '.DataTable')
          else
            fixed_header.hide()

          @

        _calculate_dist_from_top: (elem) ->
          scrollTop = $(window).scrollTop()
          elementOffset = @$(elem).offset().top
          return elementOffset - scrollTop

        detect_pagination: (event) ->
          # Don't load another page while the page is being requested from the
          # server
          return if @page_loading

          return if @$el.is ':hidden'

          view_height   = @$('.DataTable').height()
          table_height  = @$('.DataTable-table').height()
          scroll_height = @$(event.currentTarget).scrollTop()
          scroll_distance = scroll_height + view_height

          # if you've scrolled all the way to the bottom, load more results
          if scroll_distance >= table_height
            console.log 'triggering pagination event'
            @page_loading = true
            @collection.next( success: => @page_loading = false )

          @


        buildItemView: (item, ItemViewType, itemViewOptions) ->
            options = _.extend( { model: item, fields: @fields, repo: @repo, linked: @linked }, itemViewOptions )
            return new ItemViewType( options )


    return DataTableView
)
