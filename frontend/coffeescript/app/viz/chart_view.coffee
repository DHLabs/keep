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
            'click .create-new a': 'new_viz'

        initialize: ( options ) ->

            @repo = options.repo
            @fields = options.fields

            # Render the list of visualizations
            @viz_view = new VizCollectionView( options )
            @viz_view.collection.reset( options.visualizations )

            @render()

            $( window ).resize( @resize )

            @

        onShow: ->
            $( window ).trigger( 'resize' )

        new_viz: ->

            # Pass in the current repo, list of fields for this repo,
            # and a callback for successful creation.
            options =
                repo: @repo
                fields: @fields
                success_callback: null

            # Create the modal and display it!
            @modalView = new NewVizModal( options )
            $('.modal').html( @modalView.render().el )

            @

        render: ->

            # Loop through each visualization and render it!
            for viz in @viz_view.collection.models
                @graph( viz )

            @

        graph: ( viz ) ->

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
