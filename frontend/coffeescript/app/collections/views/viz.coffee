define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette'

          # Model stuff
          'app/collections/viz' ],

( $, _, Backbone, Marionette, VizCollection ) ->

    class VizItemView extends Backbone.Marionette.ItemView
        tagName: 'div'
        template: _.template( '''
                        <svg id='viz-<%= id %>'></svg>
                        <a href='#' data-id='<%= id %>' class='btn btn-small btn-delete'>
                            <i class='fa fa-trash'></i>
                            Delete
                        </a>&nbsp;
                    ''' )


    class VizCollectionView extends Backbone.Marionette.CollectionView
        el: $( '#analytics-viz-list' )
        itemView: VizItemView
        collection: new VizCollection

        buildItemView: ( item, ItemViewType, itemViewOptions ) ->
            options = _.extend( { model: item },
                                itemViewOptions,
                                { className: 'eight columns' } )

            return new ItemViewType( options )


    return VizCollectionView

)
