define( [ 'jquery',
          'vendor/underscore',
          'vendor/backbone-min',
          'leaflet',
          'leaflet_heatmap',
          'leaflet_cluster' ],

( $, _, Backbone, L ) ->

    class MapView extends Backbone.View
        name:           "MapView"


        el:             $( '#map_viz' )
        btn:            $( '#map_btn' )

        map_headers:    undefined
        map:            undefined

        # Time step variables
        step_clicked:  false
        step_current: 0
        num_steps: 0
        quantum: 0

        is_paused: true
        reset: false

        progress: 0
        progress_range: 100.0

        DataView::pL = []
        DataView::pLStyle =
            color: "blue"
            weight: 0.5
            opacity: 1
            smoothFactor: 0.5

        # Time step HTML values
        $( '#fpsbox' ).html( $( '#fps' ).val() )
        $( '#playtimebox' ).html( $( '#playtime' ).val() )

        controls: null
        current_controls: null
        playback: null

        events:
            "change #fps":              "update_fps"
            "change #playtime":         "update_playtime"
            "change #progress_bar":     "update_progress"

            "click #time_step":         "time_step"
            "click #auto_step":         "auto_step"
            "click #pause":             "pause_playback"
            "click #reset":             "reset_playback"

            "click #time_c":            "time_c"
            "click #clear":             "clear_lines"

        initialize: ( options ) ->
            @parent = options.parent
            @data   = options.data
            @form   = options.form

            @_detect_headers( @form.attributes.children )

            @mapIcon = L.icon(
                        iconUrl: '//keep-static.s3.amazonaws.com/img/leaflet/marker-icon.png'
                        iconRetinaUrl: '//keep-static.s3.amazonaws.com/img/leaflet/marker-icon@2x.png'
                        iconSize: [25, 41]
                        iconAnchor: [12, 41]
                        popupAnchor: [1, -34]
                        shadowUrl: '//keep-static.s3.amazonaws.com/img/leaflet/marker-shadow.png'
                        shadowSize: [41, 41]
                        shadowAnchor: [15, 41] )

            if @map_headers?
                @btn.removeClass( 'disabled' )
                @render()

                # min and max time in milliseconds for the array
                @min_time = Date.parse( @data.models[0].get('timestamp') )
                @max_time = Date.parse( @data.models[ @data.models.length - 1 ].get('timestamp') )

                # use start and end time fields if they are not empty
                if start_date.value?.length > 0
                    @min_time = Date.parse( start_date.value )

                if end_date.value?.length > 0
                    @max_time = Date.parse( end_date.value )

                # split the time into frames based on fps * playtime
                @num_steps = $( '#fps' ).val() * $( '#playtime' ).val()

                # calc size of quantum
                @quantum = Math.floor( (@max_time - @min_time) / @num_steps )

                # set upper and lower bound
                @lower_bound = @min_time
                @upper_bound = @min_time + @quantum

        _detect_headers: ( root ) ->

            for field in root
                if field.type in [ 'group' ]
                    @_detect_headers( field.children )

                # Detect geopoints
                if field.type in [ 'geopoint' ]
                    @map_headers = field
                    return

        render: () ->
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
            valid_count = 0
            for datum in @data.models

                geopoint = datum.get( 'data' )[ @map_headers.name ]
                if not geopoint?
                    continue

                geopoint = geopoint.split( ' ' )
                if isNaN( geopoint[0] ) or isNaN( geopoint[1] )
                    continue

                center[0] += parseFloat( geopoint[0] )
                center[1] += parseFloat( geopoint[1] )
                valid_count += 1

            if valid_count == 0
                @map_enabled = false
                $( '#map_btn' ).addClass( 'disabled' )
                $( '#map' ).hide()
                return @

            center[0] = center[0] / valid_count
            center[1] = center[1] / valid_count

            @map = L.map( 'map' ).setView( center, 10 )

            L.tileLayer( 'http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
                            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
                            maxZoom: 18 }).addTo( @map )

            heatmapData = []
            @markers = []
            @constrained_markers = new L.layerGroup()
            @marker_layer = new L.MarkerClusterGroup()
            for datum in @data.models
                geopoint = datum.get( 'data' )[ @map_headers.name ]

                if not geopoint?
                    continue

                geopoint = geopoint.split( ' ' )
                if isNaN( geopoint[0] ) or isNaN( geopoint[1] )
                    continue

                marker = L.marker( [geopoint[0], geopoint[1]], {icon: @mapIcon})
                marker.data = datum.get( 'data' )
                marker.timestamp = datum.get( 'timestamp' )

                html = ''
                for key, value of marker.data
                    html += "<div><strong>#{key}:</strong> #{value}</div>"
                marker.bindPopup( html )

                @marker_layer.addLayer( marker )
                @constrained_markers.addLayer( marker )

                heatmapData.push(
                    lat: geopoint[0]
                    lon: geopoint[1]
                    value: 1 )

            @heatmap.addData( heatmapData )

            @map.addLayer( @heatmap )
            @map.addLayer( @marker_layer )
            @map.addLayer( @constrained_markers )

            layers =
                'Markers': @marker_layer
                'Heatmap': @heatmap
                'Constrained': @constrained_markers

            controls = L.control.layers( null, layers, { collapsed: false } )
            controls.addTo( @map )
            @

        auto_step: (event) =>
            # continuously call time step
            auto = () =>
                if not @is_paused
                    @time_step()
            @playback = setInterval( auto, 1000/fps.value )

        pause_playback: (event) ->
            if @is_paused
                $( '#pause' ).html( "<i class='icon-pause'></i>" )
                @is_paused = false
            else
                $( '#pause' ).html( "<i class='icon-play'></i>" )
                @is_paused = true

        # resets playback
        reset_playback: (event) ->
            if @playback?
                clearInterval( @playback )
                @playback = null

            # set initial lower and upper bound of our current quantum
            @lower_bound = @min_time
            @upper_bound = @min_time + @quantum

            @step_current = 0

            $( '#current_time' ).html( '' )

            @progress = 0
            $( '#progress_bar' ).val( 0 )

            $( '#pause_btn' ).html( '<icon class="icon-play"></i>' )
            @is_paused = false

        update_fps: () ->
            $( '#fpsbox' ).html( fps.value )
            @


        update_playtime: () ->
            $( '#playtimebox' ).html( playtime.value )
            @

        # method called when progress bar changes - resets lower/upper bounds
        update_progress: () ->
            if @step_clicked == true and @reset == false
                if (@is_paused == false)
                    @is_paused = true

                @progress = progress_bar.value
                #alert ( (@max_time - @min_time))
                @upper_bound = (@progress/@progress_range * (@max_time - @min_time) + @min_time)
                if (cumulativeCheck.checked == true)
                    @lower_bound = @min_time
                else
                    @lower_bound = @upper_bound - @quantum
                current_time.innerHTML = new Date(@lower_bound) + " through " + new Date(@upper_bound)
                @is_paused = false
                @render()

        clear_lines: (event) ->
            for i of @map._layers
                unless @map._layers[i]._path is `undefined`
                    try
                        @map.removeLayer @map._layers[i]
                    catch e
                        console.log "problem with " + e + @map._layers[i]

        time_step: (event) ->
            # only call render for the number of quantums that we have
            @step_current += 1
            if @step_current <= @num_steps

                @constrained_markers.eachLayer( ( layer ) =>
                    timestamp = Date.parse( layer.timestamp )

                    if @lower_bound <= timestamp <= @upper_bound
                        layer.setOpacity( 1.0 )
                    else
                        layer.setOpacity( 0.0 )
                )

                # display the range of the current quantum
                lower_bound_str = new Date( @lower_bound )
                upper_bound_str = new Date( @upper_bound )

                $( '#current_time' ).html( "#{lower_bound_str} through #{upper_bound_str}" )

                @progress = (@progress_range * ((@upper_bound-@min_time) / (@max_time-@min_time)))

                $( '#progress_bar > .bar' ).width( @progress + '%' )

            # move on to the next quantum
            #if cumulativeCheck.checked == false
            #   @lower_bound += @quantum

            @upper_bound += @quantum


        time_c: (event) ->
            val = $("#tc_input").val()
            con = $("input:radio[name=const]:checked").val()
            time = $("input:radio[name=time]:checked").val()
            minutes = 1000 * 60
            hours = minutes * 60
            days = hours * 24
            secs = undefined
            for i of @map._layers
                unless @map._layers[i]._path is `undefined`
                    try
                        @map.removeLayer @map._layers[i]
                    catch e
                        console.log "problem with " + e + @map._layers[i]
            if con is "day"
                secs = days
            else if con is "hour"
                secs = hours
            else secs = minutes  if con is "minute"
            _ref5 = @data.models
            _j = 0
            _len1 = _ref5.length

            while _j < (_len1 - 1)
                datum = _ref5[_j]
                parseDate = d3.time.format("%Y-%m-%dT%H:%M:%S").parse
                if time is "date"
                    try
                        start = Date.parse(@data.models[_j].attributes.data.Time)
                    catch err
                        start = null
                else
                    start = parseDate(@data.models[_j].get("timestamp"))
                d = Math.floor(start / secs)
                geopoint = datum.get("data")[@map_headers].split(" ")
                @pL = []
                @pL.push [parseFloat(geopoint[0]), parseFloat(geopoint[1])]
                _k = _j + 1
                _len1 = _ref5.length

                while _k < _len1
                    break  if start = null
                    datum2 = _ref5[_k]
                    parseDate = d3.time.format("%Y-%m-%dT%H:%M:%S").parse
                    if time is "date"
                        try
                            start2 = Date.parse(@data.models[_k].attributes.data.Time)
                        catch err
                            start2 = null
                    else
                        start2 = parseDate(@data.models[_k].get("timestamp"))
                    d2 = Math.floor(start2 / secs)
                    geopoint = datum2.get("data")[@map_headers].split(" ")
                    if val >= Math.abs(d - d2)
                        @pL.push [parseFloat(geopoint[0]), parseFloat(geopoint[1])]
                        @poly = L.polyline(@pL, @pLStyle).addTo(@map)
                    else
                        break
                    _k++
                _j++

    return MapView
)