class DataModel extends Backbone.Model
    defaults:
        data: []

class FormModel extends Backbone.Model
    initialize: ->
        @form_id = $( '#form_id' ).html()
        @user    = $( '#user' ).html()

        @url = "/api/v1/repos/#{@form_id}/?format=json&user=#{@user}"

class DataCollection extends Backbone.Collection
    model: DataModel

    initialize: ->
        # Grab the form_id from the page
        @form_id = $( '#form_id' ).html()
        @url = "/api/v1/data/#{@form_id}/?format=json"

    comparator: ( data ) ->
        return data.get( 'timestamp' )

class DataView extends Backbone.View

    # The HTML element where the viz will be rendered
    el: $( '#viz' )

    events:
        "click #yaxis_options input":   "change_y_axis"
        "click #chart_options a.btn":   "switch_viz"
        "change #sharing_toggle":       "toggle_public"
        "change #fps":                  "update_fps"
        "change #playtime":             "update_playtime"
        "click #time_step a.btn":       "time_step"
        "click #auto_step a.btn":       "auto_step"
        "click #time_static a.btn":     "time_static"
        "click #pause a.btn":           "pause_playback"

    # Current list of survey data
    data: new DataCollection()

    # Current form that this data was for
    form: new FormModel()

    # Raw data stuff
    raw_headers: [ 'uuid' ] # Headers used for the raw data table header

    # Map related stuff
    map_headers: null       # Map related headers (geopoint datatype)
    map_enabled: false      # Did we detect any geopoints in the data?
    map: null               # Map object

    # Time step variables
    step_clicked:  false
    step_current: 0
    num_steps: 0
    quantum: 0
    min_time:0
    max_time:0
    lower_bound:0
    upper_bound:0
    is_paused: false
    # Time step HTML values
    fpsbox.innerHTML= fps.value
    playtimebox.innerHTML= playtime.value
    current_constrained_layer: null

    # Yaxis chosen by the user
    yaxis: null
    chart_fields: []

    # In pixels
    width:  750
    height: 250

    initialize: ->
        # Begin render when the list is finished syncing with the server
        @listenTo( @form, 'sync', @render )
        @form.fetch()

        @data = document.initial_data

        @

    toggle_public: (event) ->
        $.post( "/repo/share/#{@form.form_id}/", {}, ( response ) =>
            if response.success
                $( event.currentTarget ).attr( 'checked', response.public )

                if response.public
                    $( '#privacy' ).html( '<img src=\'/static/img/public_repo.png\'>&nbsp;PUBLIC' )
                else
                    $( '#privacy' ).html( '<img src=\'/static/img/private_repo.png\'>&nbsp;PRIVATE' )
        )

        @

    switch_viz: (event) ->

        viz_type = $( event.currentTarget ).data( 'type' )

        # Check that the viz is enabled
        if viz_type == 'map' and not @map_enabled
            return
        else if viz_type == 'line' and @chart_fields.length == 0
            return

        $( '.active' ).removeClass( 'active' )
        $( event.currentTarget ).addClass( 'active' )

        $( '.viz-active' ).fadeOut( 'fast', ()->
            $( @ ).removeClass( 'viz-active' )

            $( '#' + viz_type + '_viz' ).fadeIn( 'fast', ()=>
                # Remember to redraw the map when we switch tabs
                if viz_type == 'map'
                    document.vizApp.map.invalidateSize( false )
            ).addClass( 'viz-active' )
        )


    auto_step: (event) =>
        # continuously call time step
        auto = () =>
            #if @is_paused
            
            if not @is_paused
                @time_step()
        setInterval auto, 1000/fps.value

    pause_playback: (event) ->
        if @is_paused
          pause_btn.innerHTML = "Pause"
          @is_paused = false
        else
          pause_btn.innerHTML = "Resume"
          @is_paused = true    

    # Reacts to click of "static_time" button in visualize.html
    # displays all markers within the chosen start/end date
    # TODO:  Due to UTC I think the times are off by 7 hours
    time_static: (event) ->
        @step_clicked = true
        length = @data.models.length
        
        # min and max time in milliseconds for the array
        @min_time = Date.parse (@data.models[0].get('timestamp'))
        @max_time = Date.parse (@data.models[length-1].get('timestamp'))

        # use start and end time fields if they are not empty
        if (start_date.value != "")
            @min_time = Date.parse( start_date.value )
        if (end_date.value != "")
            @max_time = Date.parse( end_date.value )

        # set upper and lower bound
        @lower_bound = @min_time
        @upper_bound = @max_time

        @renderMap()

    update_fps: () ->
        fpsbox.innerHTML= fps.value
        
    update_playtime: () ->
        playtimebox.innerHTML= playtime.value

    time_step: (event) ->
        # setup for the first time they click step
        if @step_clicked == false
            length = @data.models.length
            @step_clicked = true


            # min and max time in milliseconds for the array
            @min_time = Date.parse (@data.models[0].get('timestamp'))
            @max_time = Date.parse (@data.models[length-1].get('timestamp'))

            # use start and end time fields if they are not empty
            if (start_date.value != "")
                alert (start_date.value)
                @min_time = Date.parse( start_date.value )
            if (end_date.value != "")
                alert ("bye")
                @max_time = Date.parse( end_date.value )

            # split the time into frames based on fps * playtime
            @num_steps = fps.value * playtime.value
            alert(@num_steps)

            # calc size of quantum
            @quantum = Math.floor ((@max_time - @min_time) / @num_steps )
            # set initial lower and upper bound of our current quantum
            @lower_bound = @min_time
            @upper_bound = @min_time + @quantum

        # only call render for the number of quantums that we have
        @step_current += 1
        if (@step_current <= @num_steps)
            @renderMap()
            # display the range of the current quantum
            current_time.innerHTML = new Date(@lower_bound)

        # move on to the next quantum
        #alert "old lower is: " + @lower_bound
        @lower_bound += @quantum
        #alert "new lower is: " + @lower_bound
        @upper_bound += @quantum


    change_y_axis: (event) ->
        # Ensure everything else is unchecked
        $( '#yaxis_options input' ).attr( 'checked', false )
        $( event.target ).attr( 'checked', true )

        # Assign the yaxis
        @yaxis = event.target.value

        # Re-render chart
        @renderCharts()


    render: ->
        # Don't render until we get both the form & survey data
        if( !@form.attributes.children || !@data )
            return

        # Loop through the form fields and check to see what type of visualizations
        # we can do.
        for field in @form.attributes.children

            # Don't show notes in the raw data table
            if field.type not in [ 'note' ]
                @raw_headers.push( field.name )

            # Only chart fields that are some sort of number
            if field.type in [ 'decimal', 'int', 'integer' ]

                @chart_fields.push( field.name )

                # If we haven't set a default Y-axis yet, set it!
                if not @yaxis
                    @yaxis = field.name

            # Detect geopoints
            if field.type in [ 'geopoint' ]
                # Enable the map button
                $( '#map_btn' ).removeClass( 'disabled' )

                @map_enabled = true
                @map_headers = field.name

        @renderRaw()

        # Only render other vizs if we actually have data!
        if @data.models.length > 0
            # Can we render a map?
            if @map_enabled
                @renderMap()
            else
                $( '#map' ).hide()

            # Can we render any charts?
            if @chart_fields.length
                @renderCharts()
            else
                $( '#line_btn' ).addClass( 'disabled' )
        else
            # Disable all the data viz buttons if we have no data
            $( '#line_btn' ).addClass( 'disabled' )
            $( '#map_btn' ).addClass( 'disabled' )
        @

    renderRaw: ->

        $( '#raw' ).html( '' )

        html = '<table id="raw_table" class="table table-striped table-bordered">'

        html += '<thead><tr>'
        headers = ''
        for key in @raw_headers
            html += "<th>#{key}</th>"
        html += '</tr></thead>'

        # Render the actual data
        html += '<tbody>'
        for datum in @data.models

            html += '<tr>'
            for key in @raw_headers

                value = datum.get( 'data' )[ key ]

                if value
                    html += "<td>#{value}</td>"
                else
                    html += "<td>N/A</td>"

            html += '</tr>'

        html += '</tbody></table>'


        $( '#raw' ).html( html )

        # Render the table using jQuery's DataTable
        #
        # NOTE: Elements taken from DataTables blog post about using DT with
        # Bootstrap, http://www.datatables.net/blog/Twitter_Bootstrap_2
        #
        $( '#raw_table' ).dataTable(
            'sDom': "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>"
            'sPaginationType': 'bootstrap'
        )

        $.extend( $.fn.dataTableExt.oStdClasses, {
            "sWrapper": "dataTables_wrapper form-inline"
        } )

        @

    renderCharts: ->
        d3.select( 'svg' ).remove()

        # Render the yaxis options
        $( '#yaxis_options' ).html( '' )
        yaxis_tmpl = _.template( $( '#yaxis_tmpl' ).html() )
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

    renderMap: ->
        @heatmap = L.TileLayer.heatMap(
                radius: 80
                opacity: 0.8
                gradient:
                    0.45: "rgb(0,0,255)",
                    0.55: "rgb(0,255,255)",
                    0.65: "rgb(0,255,0)",
                    0.95: "yellow",
                    1.0: "rgb(255,0,0)" )

        # Calculate the center of the data
        center = [ 0, 0 ]
        for datum in @data.models
            geopoint = datum.get( 'data' )[ @map_headers ].split( ' ' )

            center[0] += parseFloat( geopoint[0] )
            center[1] += parseFloat( geopoint[1] )

        center[0] = center[0] / @data.models.length
        center[1] = center[1] / @data.models.length

        if @step_clicked == false
            @map = L.map('map').setView( center, 10 )

        L.tileLayer( 'http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
                        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
                        maxZoom: 18 }).addTo( @map )

        myIcon = L.icon(
                    iconUrl: '/static/img/leaflet/marker-icon.png'
                    iconRetinaUrl: '/static/img/leaflet/marker-icon@2x.png'
                    iconSize: [25, 41]
                    iconAnchor: [12, 41]
                    popupAnchor: [1, -34]
                    shadowUrl: '/static/img/leaflet/marker-shadow.png'
                    shadowSize: [41, 41]
                    shadowAnchor: [15, 41] )

        heatmapData = []
        @markers = []
        @constrained_markers = []
        @marker_layer = new L.MarkerClusterGroup()
        for datum in @data.models
            geopoint = datum.get( 'data' )[ @map_headers ].split( ' ' )
            timestamp = Date.parse(datum.get('timestamp'))

            marker = L.marker( [geopoint[0], geopoint[1]], {icon: myIcon})

            html = ''
            for key, value of datum.get( 'data' )
                html += "<div><strong>#{key}:</strong> #{value}</div>"
            marker.bindPopup( html )

            @marker_layer.addLayer( marker )
            constrainedMarker = L.marker( [geopoint[0], geopoint[1]], {icon: myIcon})

            if @lower_bound <= timestamp and timestamp <= @upper_bound
                @constrained_markers.push( constrainedMarker )

            heatmapData.push(
                lat: geopoint[0]
                lon: geopoint[1]
                value: 1 )

        @constrained_layer = L.layerGroup( @constrained_markers )
        @heatmap.addData( heatmapData )

        
        if (!@step_clicked)
            @map.addLayer( @heatmap )
            @map.addLayer( @marker_layer )
        if (@step_clicked)
            @map.removeLayer(@current_constrained_layer)
        @map.addLayer( @constrained_layer )
        @current_constrained_layer = @constrained_layer

        layers =
            'Markers': @marker_layer
            'Heatmap': @heatmap
            'Constrained': @constrained_layer

        # why doesn't the constrained layer disappear??
        
        
        controls = L.control.layers( null, layers, { collapsed: false } )
        if (!@step_clicked)
            controls.addTo( @map )
