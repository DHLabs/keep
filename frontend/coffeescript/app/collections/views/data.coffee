define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette'

          # Model stuff
          'app/collections/data' ],

( $, _, Backbone, Marionette, DataCollection ) ->

    class DataItemView extends Backbone.Marionette.ItemView
        tagName: 'li'
        template: _.template( '''
            <div class='study-settings'>
                <a href='#' data-name='<%= name %>' data-study='<%= id %>'><i class='icon-cog'></i></a>
            </div>
            <a href='#' data-study='<%= id %>'><%= name %></a>''' )


    class DataCollectionView extends Backbone.Marionette.CollectionView
        el: '#data_list'
        itemView: StudyItemView
        collection: new DataCollection

    return DataCollectionView
)