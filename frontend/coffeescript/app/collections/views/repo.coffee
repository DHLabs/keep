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
                <i class="<%= privacy_icon %>"></i>
            </td>
            <td class='add-data'>
                <a href='<%= webform_uri %>' class='btn btn-small'>
                    <i class='fa fa-pencil'></i> Add Data
                </a>
            </td>
            <td>
                <a href='<%= uri %>'>
                    <%= name %>
                    <div class='meta-data'>
                        <% if( study ){ %>
                            <div class='study'><i class='fa fa-briefcase'></i>&nbsp;<%= study %></div>
                        <% } %>
                        <% if( description.length > 0 ) { %>
                            <div class='help-block'><%= description %></div>
                        <% } %>
                    </div>
                </a>
            </td>
            <td class='submission-count'>
                <%= submissions %>&nbsp;<i class='fa fa-file-alt'></i>
            </td>''' )

        onRender: ->
            # Apply draggable/droppable attributes to the new repo rows.
            $( @el ).draggable(
                helper: 'clone'
                opacity: 0.7
            )

            $( @el ).data( 'repo', @model.id )

            # Add filter categories to the row
            if @model.get( 'is_public' )
                $( @el ).addClass( 'public' )
            else
                $( @el ).addClass( 'private' )

            if @model.get( 'org' )? or @model.get( 'user' ) != parseInt( document.user_id )
                $( @el ).addClass( 'shared' )

            @


    class RepoCollectionView extends Backbone.Marionette.CollectionView
        el: $( '#repo_list > tbody' )
        itemView: RepoItemView
        collection: new RepoCollection

        filter: ( filter ) ->
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

            @

    return RepoCollectionView

)
