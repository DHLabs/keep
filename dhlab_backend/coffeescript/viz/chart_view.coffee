define( [ 'jquery',
          'vendor/underscore',
          'vendor/backbone-min' ],

( $, _, Backbone ) ->

    class ChartView extends Backbone.View

        name: 'ChartView'
        el: $( '#line' )

        yaxis_template = '''
            <label class="radio">
                <input type="radio" value="<%= value %>" <%= checked %>> <%= label %>
            </label>'''

        initialize: ( options ) ->
            @parent       = options.parent
            @data         = options.data
            @chart_fields = options.chart_fields

        render: ->
            d3.select( 'svg' ).remove()

            # Render the yaxis options
            $( '#yaxis_options' ).html( '' )
            yaxis_tmpl = _.template( yaxis_template )
            for option in @chart_fields
                $( '#yaxis_options' ).append( yaxis_tmpl(
                        label: option
                        value: option
                        checked: if @yaxis == option then 'checked' else ''
                ))

            # Render the actual line chart
            parseDate = d3.time.format( '%Y-%m-%dT%H:%M:%S' ).parse

            start = parseDate( @data.models[0].get( 'timestamp' ) )
            end   = parseDate( @data.models[ @data.length - 1 ].get( 'timestamp' ) )

            # Find our range
            min = null
            max = null
            for model in @data.models
                value = parseFloat( model.get( 'data' )[ @yaxis ] )

                if !min || value < min
                    min = value

                if !max || value > max
                    max = value

            x = d3.time.scale().domain( [ start, end ] ).range( [ 0, 800 ] )
            y = d3.scale.linear().domain( [ min, max ] ).range( [ 200, 0 ] )

            xAxis = d3.svg.axis().scale( x ).orient( 'bottom' )
            yAxis = d3.svg.axis().scale( y ).orient( 'left' )

            line = d3.svg.line()
                    .x( ( d ) => return x( parseDate(  d.get( 'timestamp' ) ) ) )
                    .y( ( d ) => return y( parseFloat( d.get( 'data' )[ @yaxis ] ) ))

            # Prep the SVG
            @svg = d3.select( '#line' ).append( 'svg' )
                        .attr( 'width', @width )
                        .attr( 'height', @height )
                    .append( 'g' )
                        .attr( 'transform', 'translate( 32, 16 )' )

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

    return ChartView

)
