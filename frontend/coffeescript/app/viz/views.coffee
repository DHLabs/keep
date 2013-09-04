define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'app/models/data',
          'app/models/repo',
          'app/collections/views/data',
          'app/collections/data' ],

( $, _, Backbone, Marionette, DataModel, RepoModel, DataCollectionView, DataCollection ) ->

    class VizChrome extends Backbone.Marionette.Region
        el: '#viz-chrome'


    class VizData extends Backbone.Marionette.Region
        el: '#viz-data'

        detect_scroll: ( event ) ->

            scrollTop = $( event.currentTarget ).scrollTop()
            scrollLeft = $( event.currentTarget ).scrollLeft()

            offsetTop = $( '#raw_table' ).position().top

            # Check if we've already copied the header row of the table
            # into the scroller div.
            header = $( '#fixed-header' )
            if not header.data( 'header' )?
                header_row = $( '#raw_table tr:first-child' )

                $( 'table tr', header ).append( header_row.html() )

                header.data( 'header', true )
                header.css( 'width', header_row.width() )

            # If we've scrolled past the header row of the table, make our
            # fixed header visible
            if scrollTop > offsetTop
                header.css( { left: "-#{scrollLeft}px" } ).show()
            else
                # Otherwise just hide the sucker.
                header.hide()
            @


        initialize: ( options ) ->
            @rawView = new DataCollectionView( options )
            @rawView.collection.reset( document.initial_data )
            @attachView( @rawView )

            # Bind scroll event
            $( @el ).scroll( @detect_scroll )


    # Instantiate and startup the new process.
    DataVizView = new Backbone.Marionette.Application

    DataVizView.addInitializer ( options ) ->

        @repo = new RepoModel( document.repo )

        # Add the different regions
        vizChrome = new VizChrome
        vizData   = new VizData( { fields: @repo.fields() } )

        DataVizView.addRegions(
                chrome: vizChrome
                viz: vizData )
        @

    return DataVizView
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
