$ ->
    class DataModel extends Backbone.Model
        defaults:
            data: []

    class DataCollection extends Backbone.Collection
        model: DataModel

        initialize: ->
            # Grab the form_id from the page
            @form_id = $( '#form_id' ).html()
            @url = '/api/v1/data/' + @form_id + '/?format=json'

        comparator: ( data ) ->
            return data.get( 'timestamp' )

    class DataView extends Backbone.View

        # The HTML element where the viz will be rendered
        el: $( '#viz' )

        # Current list of survey data
        data: new DataCollection()

        initialize: ->
            # Begin render when the list is finished syncing with the server
            @listenTo( @data, 'sync', @render )
            @data.fetch()

            # Prep the SVG
            @svg = d3.select( '#viz' ).append( 'svg' )
                        .attr( 'width', 850 )
                        .attr( 'height', 250 )
                        .append( 'g' )
                        .attr( 'transform', 'translate( 32, 16 )' )

            @

        render: ->
            console.log( @data )
            parseDate = d3.time.format( '%Y-%m-%dT%H:%M:%S' ).parse

            start = parseDate( @data.models[0].get( 'timestamp' ) )
            end   = parseDate( @data.models[ @data.length - 1 ].get( 'timestamp' ) )

            x = d3.time.scale().domain( [ start, end ] ).range( [ 0, 800 ] )
            y = d3.scale.linear().domain( [ 20.0, 140.0 ] ).range( [ 200, 0 ] )

            xAxis = d3.svg.axis().scale( x ).orient( 'bottom' )
            yAxis = d3.svg.axis().scale( y ).orient( 'left' )

            line = d3.svg.line()
                    .x( ( d ) => return x( parseDate(  d.get( 'timestamp' ) ) ) )
                    .y( ( d ) -> return y( parseFloat( d.get( 'data' )[ 'heart_rate' ] ) ))

            @svg.append( 'g' )
                .attr( 'class', 'x axis' )
                .attr( 'transform', 'translate( 0, 200 )' )
                .call( xAxis )

            @svg.append( "g" )
                .attr( "class", "y axis" )
                .call( yAxis )

            @svg.append( 'path' )
                .datum( @data.models )
                .attr( 'class', 'line' )
                .attr( 'd', line )

            @

    VizApp = new DataView()
