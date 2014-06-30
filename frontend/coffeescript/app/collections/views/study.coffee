define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette'

          # Model stuff
          'app/collections/study' ],

( $, _, Backbone, Marionette, StudyCollection ) ->

    class StudyItemView extends Backbone.Marionette.ItemView
        tagName: 'li'
        template: _.template( '''
            <div class='study-settings'>
                <a href='#' data-name='<%= name %>' data-study='<%= id %>'><i class='icon-cog'></i></a>
            </div>
            <a href='#' data-study='<%= id %>'><%= name %></a>''' )


    class StudyCollectionView extends Backbone.Marionette.CollectionView
        el: '#study_list'
        itemView: StudyItemView
        collection: new StudyCollection

        selected: ()->
            return $( 'li.selected > a', @el ).data( 'study' )

    return StudyCollectionView
)