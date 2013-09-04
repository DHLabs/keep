define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette'

          # Model stuff
          'app/collections/data' ],

( $, _, Backbone, Marionette, DataCollection ) ->

    class DataItemView extends Backbone.Marionette.ItemView
        tagName: 'tr'

        initialize: (options) ->
            @fields = options.fields

        template: ( model ) =>
            data = { fields: @fields, model: model }

            templ = _.template( '''
                <% _.each( fields, function( field ) { %>
                    <td><%= model.data[ field.name ] %></td>
                <% }); %><td>&nbsp;</td>''')

            return templ( data )


    class DataCollectionView extends Backbone.Marionette.CollectionView
        el: '#raw-viz #raw_table'
        itemView: DataItemView
        collection: new DataCollection

        header_template: _.template( '''
                <tr>
                <% _.each( fields, function( item ) { %>
                    <th data-field='<%= item.name %>'>
                        <%= item.name %><i class='sort-me icon-sort'></i>
                    </th>
                <% }); %>
                    <th>&nbsp;</th>
                </tr>
            ''')

        initialize: ( options )->
            @fields = options.fields
            @repo   = options.repo

            @$el.append( @header_template( options ) )
            @

        buildItemView: ( item, ItemViewType, itemViewOptions ) ->
            options = _.extend( { model: item, fields: @fields }, itemViewOptions )
            return new ItemViewType( options )

    return DataCollectionView
)