define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette'

          # Model stuff
          'app/collections/data' ],

( $, _, Backbone, Marionette, DataCollection ) ->

    class DataItemView extends Backbone.Marionette.ItemView
        tagName: 'tr'

        data_templates:
            'text':     _.template( '<td><%= data %></td>' )
            'geopoint': _.template( '<td><%= data.coordinates[1] %>, <%= data.coordinates[0] %></td>' )

        initialize: (options) ->
            @fields = options.fields

        template: ( model ) =>
            # Based on the field type, we use a specific formatter for that
            # data type.
            templ = []
            for field in @fields
                tdata = { data: model.data[ field.name ] }

                if field.type == 'geopoint'
                    templ.push( @data_templates[ field.type ]( tdata ) )
                else
                    templ.push( @data_templates[ 'text' ]( tdata ) )

            # Fix for fixed-width tables. The last td is flexible, thus making
            # the tds before it fixed.
            templ.push( '<td>&nbsp;</td>' )
            return templ.join( '' )


    class DataCollectionView extends Backbone.Marionette.CollectionView
        el: '#raw-viz #raw_table'
        itemView: DataItemView

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

            @collection = new DataCollection( options )

            @$el.append( @header_template( options ) )

            @

        buildItemView: ( item, ItemViewType, itemViewOptions ) ->
            options = _.extend( { model: item, fields: @fields }, itemViewOptions )
            return new ItemViewType( options )

    return DataCollectionView
)