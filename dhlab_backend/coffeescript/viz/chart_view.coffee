define( [ 'jquery',
          'vendor/underscore',
          'vendor/backbone-min' ],

( $, _, Backbone ) ->

    class ChartView extends Backbone.View

        name: 'ChartView'

        el: $( '#line_viz' )
        btn: $( '#line_btn' )

        events:
            "click #yaxis_options input":   "change_y_axis"

        yaxis_tmpl = _.template( '''
            <label class="radio">
                <input type="radio" value="<%= value %>" <%= checked %>> <%= label %>
            </label>''' )

        yaxis: undefined
        yaxis_fields: []

        initialize: ( options ) ->
            @parent     = options.parent
            @form       = options.form
            @data       = options.data

            @_parse_date = d3.time.format( '%Y-%m-%dT%H:%M:%S' ).parse

            @_detect_axes( @form.attributes.children )

            if @yaxis_fields.length > 0
                $( '#line_btn' ).removeClass( 'disabled' )
                @render()

        _detect_axes: ( root ) ->

            for field in root
                if field.type in [ 'group' ]
                    @_detect_types( field.children )

                # Only chart fields that are some sort of number
                if field.type in [ 'decimal', 'int', 'integer' ]
                    @yaxis_fields.push( field )

                    if not @yaxis?
                        @yaxis = field

        _x_datum: ( d ) =>
            # Render the actual line chart
            return @x( @_parse_date( d.get( 'timestamp' ) ) )

        _y_datum: ( d ) =>

            yval = parseFloat( d.get( 'data' )[ @yaxis.name ] )

            if yval is not NaN
                return @y( parseFloat( d.get( 'data' )[ @yaxis.name ] ) )
            else
                return @y( 0.0 )

        change_y_axis: (event) ->
            # Ensure everything else is unchecked
            $( '#yaxis_options input' ).attr( 'checked', false )
            $( event.target ).attr( 'checked', true )

            # Assign the yaxis
            for field in @yaxis_fields
                if field.name == event.target.value
                    @yaxis = field
                    break

            # Re-render chart
            @render()

        render: ->
            d3.select( 'svg' ).remove()

            # Render the yaxis options
            $( '#yaxis_options' ).html( '' )
            for field in @yaxis_fields
                $( '#yaxis_options' ).append( yaxis_tmpl(
                        label: field.label
                        value: field.name
                        checked: if @yaxis.name == field.name then 'checked' else ''
                ))


            start = @_parse_date( @data.models[0].get( 'timestamp' ) )
            end   = @_parse_date( @data.models[ @data.length - 1 ].get( 'timestamp' ) )

            # Find our range
            min = null
            max = null
            for model in @data.models
                value = parseFloat( model.get( 'data' )[ @yaxis.name ] )

                if !min || value < min
                    min = value

                if !max || value > max
                    max = value

            @x = d3.time.scale().domain( [ start, end ] ).range( [ 0, 800 ] )
            @y = d3.scale.linear().domain( [ min, max ] ).range( [ 200, 0 ] )

            xAxis = d3.svg.axis().scale( @x ).orient( 'bottom' )
            yAxis = d3.svg.axis().scale( @y ).orient( 'left' )

            line = d3.svg.line().x( @_x_datum ).y( @_y_datum )

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
