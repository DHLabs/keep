define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'app/collections/data',
          'app/collections/viz',
          'app/collections/views/viz',

          'app/viz/modals/new_viz',

          'd3',
          'nvd3' ],

( $, _, Backbone, Marionette,
    DataCollection, VizCollection, VizCollectionView,
    NewVizModal,
    d3, nvd3 ) ->

    class ChartItemView extends Backbone.Marionette.ItemView
        template: _.template( '''n/a''' )

    class DataChartView extends Backbone.Marionette.View
        el: '#analytics-viz'
        itemView: ChartItemView

        events:
            'click .create-new a': 'create_new_viz_event'
            'click a.btn-delete':  'delete_viz_event'

        _on_new_viz: ( model, response, options ) =>
            # Callback function called when a new viz is created through the
            # NewVizModal.
            #
            # 1. We add the new viz to our viz collection
            # 2. Update the collection view
            # 3. Then render the new viz immediately.
            #

            # 1 & 2
            model.set( {id: response.id} )
            @viz_view.collection.add( model )

            # 3!
            @render()

            # 4. Profit

            @

        initialize: ( options ) ->

            @repo = options.repo
            @fields = options.fields

            # VizCollection view will create the SVGs placeholders needed
            # to render each viz when @render is called.
            @viz_view = new VizCollectionView( options )
            @viz_view.collection.reset( options.visualizations )

            # Render each viz
            @render()

            # Correctly resize our vizs when the window is resized
            $( window ).resize( @resize )

            @

        onShow: ->
          @delegateEvents()
          $(window).trigger('resize')

        create_new_viz_event: ( event ) ->

            # Pass in the current repo, list of fields for this repo,
            # and a callback for successful creation.
            options =
                repo: @repo
                fields: @fields
                success: @_on_new_viz

            # Create the modal and display it!
            @modalView = new NewVizModal( options )
            $('.modal').html( @modalView.render().el )

            @

        delete_viz_event: ( event ) ->

            viz_id = $( event.currentTarget ).data( 'id' )
            viz = @viz_view.collection.get( viz_id )

            # If the viz exists, remove from collection view and delete
            if viz?
                @viz_view.collection.remove( viz )
                viz.destroy( {id: viz.id} )

            @

        render: ->

            # Loop through each visualization and render it!
            for viz in @viz_view.collection.models
                @graph( viz )

            @

        graph: ( viz ) ->

            # Viz sample will ajax call our data API to sample data from
            # this specific data repo. If this has been done before, it is
            # cached and can be rendered immediately. Otherwise it will
            # wait for the data before rendering.
            viz.sample( ( data ) ->

                viz_id = "#viz-#{viz.get('id')}"

                nv.addGraph( () =>

                    width  = 600
                    height = 200

                    chart = nv.models.lineChart().options({
                                height: height,
                                showXAxis: true,
                                showYAxis: true,
                                transitionDuration: 250 })

                    chart.xAxis.axisLabel( viz.get( 'x_axis' ) )
                    chart.yAxis.axisLabel( viz.get( 'y_axis' ) )

                    chart_data =
                        values: data
                        key: viz.get( 'name' )
                        color: '#F00'

                    d3.select( viz_id )
                        .attr( 'height', height )
                        .datum( [chart_data] )
                        .call( chart )

                    nv.utils.windowResize( chart.update )

                    return chart
                )
            )

        @

    return DataChartView
)
