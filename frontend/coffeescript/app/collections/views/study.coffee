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
                <a href='#' data-name='<%= name %>' data-id='<%= id %>'><i class='icon-cog'></i></a>
            </div>
            <a href='#' data-study='<%= id %>'><%= name %></a>''' )

        onRender: ->
            $( @el ).droppable(
                hoverClass: 'drop-hover'
                drop: ( event, ui ) ->
                    study_id = $( 'a', @ ).data( 'study' )
                    if not study_id?
                        study_id = null

                    repo_id = $( ui.draggable ).data( 'repo' )

                    $.ajax(
                        headers:
                            'Accept' : 'application/json'
                            'Content-Type' : 'application/json'
                        url: "/api/v1/repos/#{repo_id}"
                        type: 'PATCH',
                        data: JSON.stringify( { 'study': study_id } )
                        success: ( response, textStatus, jqXhr ) ->
                            console.log( response )
                    )
                )


    class StudyCollectionView extends Backbone.Marionette.CollectionView
        el: '#study_list'
        itemView: StudyItemView
        collection: new StudyCollection

        initialize: ->
            @collection.reset( document.study_list )
            @render()
)