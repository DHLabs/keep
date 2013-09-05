define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'app/models/data',
          'app/models/repo',

          'app/viz/raw_view' ],

( $, _, Backbone, Marionette, DataModel, RepoModel, DataRawView ) ->

    class VizTabs extends Backbone.Marionette.View
        el: '#viz-options'

        events:
            'click li': 'switch_event'

        switch_event: ( event ) ->
            target = $( event.currentTarget )

            if @selected().attr( 'id' ) == target.attr( 'id' )
                return

            if target.hasClass( 'disabled' )
                return

            @selected().removeClass( 'active' )
            target.addClass( 'active' )

            @trigger( 'switch:' + target.data( 'type' ) )

        selected: () ->
            # Return the currently selected tab
            return $( 'li.active', @el )


    class VizChrome extends Backbone.Marionette.Region
        el: '#viz-chrome'

        initialize: ( options ) ->
            view = new VizTabs()
            @attachView( view )


    # Instantiate and startup the new process.
    DataVizApp = new Backbone.Marionette.Application

    DataVizApp.addInitializer ( options ) ->

        @repo = new RepoModel( document.repo )

        # Add the different regions
        vizChrome = new VizChrome
        rawView   = new DataRawView( { repo: @repo.id, fields: @repo.fields() } )

        DataVizApp.addRegions(
                chrome: vizChrome
                viz: rawView )

        # Handle application wide events
        vizChrome.currentView.on( 'switch:raw', () ->
            rawView.switch_view( 'raw' ) )

        vizChrome.currentView.on( 'switch:map', () ->
            rawView.switch_view( 'map' ) )

        vizChrome.currentView.on( 'switch:line', () ->
            rawView.switch_view( 'line' ) )

        vizChrome.currentView.on( 'switch:settings', () ->
            rawView.switch_view( 'settings' ) )

        @

    return DataVizApp
)

remove_permissions= (div,username) ->
    $.ajax({
        type: "DELETE",
        url: "/repo/user_share/"+$( '#form_id' ).html()+"/?username=" + username,
        data: "username=" + username,
        success: () ->
            div.parentNode.parentNode.innerHTML = ""

    })
    @
