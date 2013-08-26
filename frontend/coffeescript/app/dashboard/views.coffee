define( [ 'jquery',
          'underscore',
          'backbone' ],

( $, _, Backbone ) ->

    class RepoCollection extends Backbone.Collection
        initialize: ->
            @url = '/api/v1/repos'

        parse: ( response ) ->
            return response.objects


    class DashboardView extends Backbone.View
        el: $( '#dashboard' )

        repos: new RepoCollection()
        repo_list: $( '#repo_list' )

        events:
            "click #studies ul li a":   "refresh_repos"
            "click #filters li a":      "apply_filters"

        repo_tmpl  = _.template( '''
            <tr class="<%= filters %>">
                <td class='privacy'>
                    <%= privacy_icon %>
                </td>
                <td class='add-data'>
                    <a href='<%= webform %>' class='btn btn-small'>
                        <i class='icon-pencil'></i> Add Data
                    </a>
                </td>
                <td>
                    <a href='<%= repo_url %>'>
                        <%= repo_name %>
                        <div class='help-block'>
                            <%= repo_description %>
                        </div>
                    </a>
                </td>
                <td class='submission-count'>
                    <%= repo_submissions %>&nbsp;<i class='icon-file-alt'></i>
                </td>
            </tr>''' )

        apply_filters: (event) ->
            filter = $( event.currentTarget ).data( 'filter' )

            if filter == 'all'
                $( 'tr', @repo_list ).fadeIn( 'fast' )
            else
                $( 'tr', @repo_list ).each( ()->
                    if $( @ ).hasClass( filter )
                        $( @ ).fadeIn( 'fast' )
                    else
                        $( @ ).fadeOut( 'fast' )
                )

            $( '#filters .selected' ).removeClass( 'selected' )
            $( event.currentTarget ).parent().addClass( 'selected' )

        initialize: ->
            @listenTo( @repos, 'sync', @render )

        refresh_repos: (event) ->
            # Fetch repositories for a given study.
            # If "All Diaries" is selected, fetch repositories

            study_id = $( event.currentTarget ).data( 'study' )
            if study_id?
                @repos.fetch( {'data': { 'study': 1 } } )
            else
                @repos.fetch()

            $( '#studies .selected' ).removeClass( 'selected' )
            $( event.currentTarget ).parent().addClass( 'selected' )

            @

        render: ->
            @repo_list.empty()
            for repo in @repos.models

                filters = []

                if repo.get( 'is_public' )
                    privacy_icon = '<icon class="icon-unlock"></i>'
                    filters.push( 'public' )
                else
                    privacy_icon = '<icon class="icon-lock"></i>'
                    filters.push( 'private' )

                if repo.get( 'org' )
                    filters.push( 'shared' )

                @repo_list.append( repo_tmpl(
                        filters: filters.join( ' ' )
                        privacy_icon: privacy_icon
                        webform: '#'
                        repo_url: '#'
                        repo_name: repo.get( 'name' )
                        repo_description: repo.get( 'description' )
                        repo_submissions: '10'
                    ) )
            @

    return DashboardView
)