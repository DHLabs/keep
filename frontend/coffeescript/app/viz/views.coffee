define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'app/models/data',
          'app/models/repo',

          'app/viz/raw_view' ],

( $, _, Backbone, Marionette, DataModel, RepoModel, DataRawView ) ->

    class VizChrome extends Backbone.Marionette.Region
        el: '#viz-chrome'


    # Instantiate and startup the new process.
    DataVizApp = new Backbone.Marionette.Application

    DataVizApp.addInitializer ( options ) ->

        @repo = new RepoModel( document.repo )

        # Add the different regions
        vizChrome = new VizChrome
        vizData   = new DataRawView( { repo: @repo.id, fields: @repo.fields() } )

        DataVizApp.addRegions(
                chrome: vizChrome
                viz: vizData )
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
