define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette'

          # Model stuff
          'app/collections/repo' ],

( $, _, Backbone, Marionette, RepoCollection ) ->

    class RepoItemView extends Backbone.Marionette.ItemView
        tagName: 'tr'

        template: _.template( '''
            <td class='privacy'>
                <%= privacy_icon %>
            </td>
            <td class='add-data'>
                <a href='<%= webform_uri %>' class='btn btn-small'>
                    <i class='icon-pencil'></i> Add Data
                </a>
            </td>
            <td>
                <a href='<%= uri %>'>
                    <%= name %>
                    <div class='help-block'>
                        <%= description %>
                    </div>
                </a>
            </td>
            <td class='submission-count'>
                <%= submissions %>&nbsp;<i class='icon-file-alt'></i>
            </td>''' )

        onRender: ->
            # Apply draggable/droppable attributes to the new repo rows.
            $( @el ).draggable(
                helper: 'clone'
                opacity: 0.7
            )

            # Add filter categories to the row
            console.log( @model )
            if @model.get( 'is_public' )
                $( @el ).addClass( 'public' )
            else
                $( @el ).addClass( 'private' )

            if @model.get( 'org' )?
                $( @el ).addClass( 'shared' )

            @


    class RepoCollectionView extends Backbone.Marionette.CollectionView
        el: $( '#repo_list > tbody' )
        itemView: RepoItemView
        collection: new RepoCollection

        initialize: ->
            @collection.reset( document.repo_list )
            @render()

        filter: ( filter ) ->
            console.log( "Filtering #{filter}" )

            if filter == 'all'
                $( 'tr', @el ).fadeIn( 'fast' )
            else
                $( 'tr', @el ).each( ()->
                    if $( @ ).hasClass( filter )
                        $( @ ).fadeIn( 'fast' )
                    else
                        $( @ ).fadeOut( 'fast' )
                )

            @current_filter = filter

            @

        refresh: ( study ) ->
            # Fetch repositories for a given study.
            # If "All Diaries" is selected, fetch all repositories
            fetch_options =
                success: @render
                reset: true

            fetch_options[ 'data' ] = { study: study } if study?

            @collection.fetch( fetch_options )

    return RepoCollectionView

)