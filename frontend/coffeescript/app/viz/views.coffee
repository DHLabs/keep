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

            # Copy the header row of the table into the scroller div.
            header = $( '#fixed-header' )
            header_row = $( '#raw_table tr:first-child' )
            $( 'table tr', header ).empty().append( header_row.html() )
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
            # Bind scroll event to handle the fixed-header rendering.
            $( @el ).scroll( @detect_scroll )

            # Initialize and create the DataCollectionView.
            @rawView = new DataCollectionView( options )
            @attachView( @rawView )

            # Attach events where necessary.
            @rawView.on( 'render', ()->
                $( 'th', @el ).click( (event) =>

                    el = $( event.currentTarget )

                    field = el.data( 'field' )
                    order = el.data( 'order' )

                    # Permutate through the ordering options for the sort.
                    if not order?
                        order = 'desc'
                        $( 'i', el ).removeClass( 'icon-sort icon-sort-up' ).addClass( 'icon-sort-down' )
                    else if order == 'desc'
                        order = 'asc'
                        $( 'i', el ).removeClass( 'icon-sort-down' ).addClass( 'icon-sort-up' )
                    else if order == 'asc'
                        order = null
                        $( 'i', el ).removeClass( 'icon-sort-up' ).addClass( 'icon-sort' )

                    el.data( 'order', order )
                    @collection.sort(
                        repo: @repo
                        field: field
                        order: order )
                )
            )

            # Load up the intial set of data to render.
            @rawView.collection.reset( document.initial_data )


    # Instantiate and startup the new process.
    DataVizView = new Backbone.Marionette.Application

    DataVizView.addInitializer ( options ) ->

        @repo = new RepoModel( document.repo )

        # Add the different regions
        vizChrome = new VizChrome
        vizData   = new VizData( { repo: @repo.id, fields: @repo.fields() } )

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
