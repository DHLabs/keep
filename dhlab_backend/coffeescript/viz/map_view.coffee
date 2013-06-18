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
        controls:       undefined
        playback:       undefined

        start_date:     $( '#start_date' )
        end_date:       $( '#end_date' )

        # Time step variables
        step_current: 0
        num_steps: 0
        quantum: 0

        is_paused: true

        progress: 0

        DataView::pL = []
        DataView::pLStyle =
            color: "blue"
            weight: 0.5
            opacity: 1
            smoothFactor: 0.5

        events:
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
                if @start_date.val().length > 0
                    @min_time = Date.parse( @start_date.val() )
                else
                    @min_time = Date.parse( @data.models[0].get('timestamp') )

                    now = new Date( @min_time )
                    day      = ( '0' + now.getDate() ).slice( -2 )
                    month    = ( '0' + (now.getMonth() + 1) ).slice( -2 )

                    @start_date.val( now.getFullYear() + '-' + month + '-' + day )

                if @end_date.val().length > 0
                    @max_time = Date.parse( @end_date.val() )
                else
                    @max_time = Date.parse( @data.models[ @data.models.length - 1 ].get('timestamp') )

                    now = new Date( @max_time )
                    day      = ( '0' + now.getDate() ).slice( -2 )
                    month    = ( '0' + (now.getMonth() + 1) ).slice( -2 )

                    @end_date.val( now.getFullYear() + '-' + month + '-' + day )

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

            # Create Leaflet map and setup markers, connectiosn and cluster layer
            center[0] = center[0] / valid_count
            center[1] = center[1] / valid_count

            @map = L.map( 'map' ).setView( center, 10 )
            L.tileLayer( 'http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
                            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
                            maxZoom: 18 }).addTo( @map )

            # Setup heatmap
            @heatmap = L.TileLayer.heatMap( { radius: 42, opacity: 0.8 } )
            heatmap_value = 1.0 / @data.models.length

            heatmapData = []
            @markers        = new L.layerGroup()
            @clusters       = new L.MarkerClusterGroup()
            @connections    = new L.layerGroup()

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

                @markers.addLayer( marker )
                @clusters.addLayer( marker )

                heatmapData.push(
                    lat: geopoint[0]
                    lon: geopoint[1]
                    count: heatmap_value )

            # By default we'll have the heatmap layer enabled and everything
            # else disabled
            @heatmap.addData( heatmapData )
            @map.addLayer( @heatmap )

            layers =
                'Clusters': @clusters
                'Connections': @connections
                'Heatmap': @heatmap
                'Markers': @markers

            @controls = L.control.layers( null, layers, { collapsed: false } )
            @controls.addTo( @map )

            @

        pause_playback: (event) ->
            if @is_paused
                $( '#pause' ).html( "<i class='icon-pause'></i>" )
                @is_paused = false

                # Start up playback interval if it's not already started up.
                if not @playback?
                    auto = () =>
                        @time_step() if not @is_paused

                    @playback = setInterval( auto, 1000.0 / $( '#fps' ).val() )

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

            $( '#progress_bar > .bar' ).width( 0 )

            $( '#pause_btn' ).html( '<icon class="icon-play"></i>' )
            @is_paused = false

        clear_lines: (event) ->
            for i of @map._layers
                unless @map._layers[i]._path is `undefined`
                    try
                        @map.removeLayer @map._layers[i]
                    catch e
                        console.log "problem with " + e + @map._layers[i]

        time_step: (event) ->

            @step_current += 1

            # If we've made it past the number steps, pause the playback and
            # return.
            if @step_current > @num_steps
                @is_paused = true
                return @

            # Go through each marker in the layer and enable/disable the
            # marker if it meets our timestamp constraints.
            last_marker = undefined
            @markers.eachLayer( ( layer ) =>
                timestamp = Date.parse( layer.timestamp )

                if @lower_bound <= timestamp <= @upper_bound
                    layer.setOpacity( 1.0 )
                    last_marker = layer
                else
                    layer.setOpacity( 0.0 )
            )

            # Pan to the last marker that was enabled
            @map.panTo( last_marker.getLatLng() ) if last_marker?

            # Calculate the percent progress we have progressed.
            @progress = 100 * ( @upper_bound - @min_time ) / ( @max_time - @min_time )

            # display the range of the current quantum
            lower_bound_str = new Date( @lower_bound )
            upper_bound_str = new Date( @upper_bound )

            $( '#current_time' ).html( "#{lower_bound_str} through #{upper_bound_str}" )
            $( '#progress_bar > .bar' ).width( "#{@progress}%" )

            @upper_bound += @quantum

            @

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