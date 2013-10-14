define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',
          'leaflet',

          # Models/collections/etc
          'app/collections/data'

          # Leaflet plugins
          'leaflet_cluster',
          'leaflet_heatmap' ],

( $, _, Backbone, Marionette, L, DataCollection ) ->

    mapIcon = L.icon(
                iconUrl: '//keep-static.s3.amazonaws.com/img/leaflet/marker-icon.png'
                iconRetinaUrl: '//keep-static.s3.amazonaws.com/img/leaflet/marker-icon@2x.png'
                iconSize: [25, 41]
                iconAnchor: [12, 41]
                popupAnchor: [1, -34]
                shadowUrl: '//keep-static.s3.amazonaws.com/img/leaflet/marker-shadow.png'
                shadowSize: [41, 41]
                shadowAnchor: [15, 41] )

    class MarkerItemView extends Backbone.Marionette.ItemView
        initialize: (options) ->
            @fields = options.fields

        template: ( model ) =>
            data = { fields: @fields, model: model }

            templ = _.template( '''
                <% _.each( fields, function( field ) { if( field.type != 'geopoint' ) { %>
                    <div><%= field.name %>: <%= model.data[ field.name ] %></div>
                <% }}); %><td>&nbsp;</td>''')

            return templ( data )


    class DataMapView extends Backbone.Marionette.CollectionView
        el: '#map-viz'
        itemView: MarkerItemView

        _detect_headers: ( fields ) ->
            @map_headers = []
            @selected_header = null

            for field in fields
                if field.type in [ 'geopoint' ]
                    @map_headers.push( field )

                    if not @selected_header?
                        @selected_header = field

                else if field.label.length == 3
                    if field.label.search( 'lat' ) != -1
                        console.log(field)
                        @map_headers.push( field )
                    else if field.label.search( 'lng' ) != -1
                        console.log(field)
                        @map_headers.push( field )

            # This means there were no geopoints... attempt to find an lat/lng
            # combo between two columns
            # TODO: Support separate lat/lngs somehow. Perhaps introduce a merging utility?
            # if not @selected_header?
            #     @selected_header = {}
            #     for field in @map_headers
            #         if field.label.search( 'lat' ) != -1
            #             @selected_header.lat = field
            #         else if field.label.search( 'lng' ) != -1
            #             @selected_header.lng = field

        _geopoint: ( datum ) ->

            geopoint = undefined

            if @selected_header.location?

                geopoint = datum.get( 'data' )[ @selected_header.location.name ]

                if not geopoint?
                    return null

                geopoint = geopoint.split( ' ' )[0..2]

                if isNaN( geopoint[0] ) or isNaN( geopoint[1] )
                    return null

            else
                geopoint = [ datum.get( 'data' )[ @selected_header.lat.name ],
                             datum.get( 'data' )[ @selected_header.lng.name ] ]

            geopoint[0] = parseFloat( geopoint[0] )
            geopoint[1] = parseFloat( geopoint[1] )

            if isNaN( geopoint[0] ) or isNaN( geopoint[1] )
                return null

            return geopoint

        _resize_map: () =>
            $( '#map' ).css( { 'height': ( @$el.parent().height() - 20 ) + 'px' } )
            @map.invalidateSize( false ) if @map?

        initialize: ( options ) ->
            # Set the height of the map to match the full height of the browser
            @_resize_map()
            $( window ).resize( @_resize_map )

            # Setup and initialize our data collection model.
            @fields = options.fields
            @collection = new DataCollection( options )
            @_detect_headers( @fields )

            # Setup the map itself
            # TODO: Pick a smart default location to look at. Maybe the user's
            # current location?
            @map = L.map( 'map' ).setView( [ 0, 0 ], 5 )
            L.tileLayer( 'http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
                         attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
                         maxZoom: 18 }).addTo( @map )

            # Create and initialize the different layers we'll have.
            @heatmap = L.TileLayer.heatMap( { radius: 24, opacity: 0.8 } )
            @markers = new L.layerGroup()
            @clusters = new L.MarkerClusterGroup()
            @connections = new L.layerGroup()

            layers =
                'Clusters': @clusters
                'Connections': @connections
                'Heatmap': @heatmap
                'Markers': @markers

            @controls = L.control.layers( null, layers, { collapsed: false } )
            @controls.addTo( @map )

            # Listen to events
            @map.on( 'moveend', @refresh_viewport )

            # Clear all our markers when we get another set of markers.
            @collection.on( 'reset', ()=>
                @markers.clearLayers()
                @clusters.clearLayers() )
            @

        appendHtml: (collectionView, itemView, index) ->
            # If we could not find any geofields or the user has not
            # specified an existing one, don't do anything with the
            # data.
            if not collectionView.selected_header?
                return

            # Instead of appending these views into the DOM, place them in the
            # map instead!
            point = itemView.model.geopoint( collectionView.selected_header )
            if not point?
                return @

            marker = L.marker( point, {icon: mapIcon} )
            marker.bindPopup( itemView.el )

            # Add marker to our different layers
            collectionView.markers.addLayer( marker )
            collectionView.clusters.addLayer( marker )

        buildItemView: ( item, ItemViewType, itemViewOptions ) ->
            options = _.extend( { model: item, fields: @fields }, itemViewOptions )
            return new ItemViewType( options )

        onShow: () ->
            @map.invalidateSize( false )

        refresh_viewport: ( event ) =>
            # If we could not find any geofields or the user has not
            # specified an existing one, don't do anything with the
            # data.
            if not @selected_header?
                return

            # Everytime we move around, grab new data from the server and
            # refresh the viewport!
            bounds = event.target.getBounds()
            @collection.fetch(
                reset: true
                data:
                    geofield: @selected_header.name
                    bbox: bounds.toBBoxString() )

    return DataMapView
)

### OLD PLAYBACK CODE. ###

# pause_playback: (event) ->
# if @is_paused
#     $( '#pause' ).html( "<i class='icon-pause'></i>" )
#     @is_paused = false

#     # Start up playback interval if it's not already started up.
#     if not @playback?
#         auto = () =>
#             @time_step() if not @is_paused

#         @playback = setInterval( auto, 1000.0 / $( '#fps' ).val() )

# else
#     $( '#pause' ).html( "<i class='icon-play'></i>" )
#     @is_paused = true
# # resets playback
# reset_playback: (event) ->
#     if @playback?
#         clearInterval( @playback )
#         @playback = null

#     # set initial lower and upper bound of our current quantum
#     @lower_bound = @min_time
#     @upper_bound = @min_time + @quantum

#     @step_current = 0

#     $( '#current_time' ).html( '' )

#     $( '#progress_bar > .bar' ).width( 0 )

#     $( '#pause_btn' ).html( '<icon class="icon-play"></i>' )
#     @is_paused = false

# clear_lines: (event) ->
#     for i of @map._layers
#         unless @map._layers[i]._path is `undefined`
#             try
#                 @map.removeLayer @map._layers[i]
#             catch e
#                 console.log "problem with " + e + @map._layers[i]

# time_step: (event) ->

#     @step_current += 1

#     # If we've made it past the number steps, pause the playback and
#     # return.
#     if @step_current > @num_steps
#         @is_paused = true
#         return @

#     # Go through each marker in the layer and enable/disable the
#     # marker if it meets our timestamp constraints.
#     last_marker = undefined
#     @markers.eachLayer( ( layer ) =>

#         if @lower_bound <= layer.timestamp <= @upper_bound
#             layer.setOpacity( 1.0 )
#             last_marker = layer
#         else
#             layer.setOpacity( 0.0 )
#     )

#     # Pan to the last marker that was enabled
#     @map.panTo( last_marker.getLatLng() ) if last_marker?

#     # Calculate the percent progress we have progressed.
#     @progress = 100 * ( @upper_bound - @min_time ) / ( @max_time - @min_time )

#     # display the range of the current quantum
#     lower_bound_str = new Date( @lower_bound )
#     upper_bound_str = new Date( @upper_bound )

#     $( '#current_time' ).html( "#{lower_bound_str} through #{upper_bound_str}" )
#     $( '#progress_bar > .bar' ).width( "#{@progress}%" )

#     @upper_bound += @quantum

#     @

# time_c: (event) ->
#     val = $("#tc_input").val()
#     con = $("input:radio[name=const]:checked").val()
#     time = $("input:radio[name=time]:checked").val()
#     minutes = 1000 * 60
#     hours = minutes * 60
#     days = hours * 24
#     secs = undefined
#     for i of @map._layers
#         unless @map._layers[i]._path is `undefined`
#             try
#                 @map.removeLayer @map._layers[i]
#             catch e
#                 console.log "problem with " + e + @map._layers[i]
#     if con is "day"
#         secs = days
#     else if con is "hour"
#         secs = hours
#     else secs = minutes  if con is "minute"
#     _ref5 = @data.models
#     _j = 0
#     _len1 = _ref5.length

#     while _j < (_len1 - 1)
#         datum = _ref5[_j]
#         parseDate = d3.time.format("%Y-%m-%dT%H:%M:%S").parse
#         if time is "date"
#             try
#                 start = Date.parse(@data.models[_j].attributes.data.Time)
#             catch err
#                 start = null
#         else
#             start = parseDate(@data.models[_j].get("timestamp"))
#         d = Math.floor(start / secs)
#         geopoint = datum.get("data")[@map_headers].split(" ")
#         @pL = []
#         @pL.push [parseFloat(geopoint[0]), parseFloat(geopoint[1])]
#         _k = _j + 1
#         _len1 = _ref5.length

#         while _k < _len1
#             break  if start = null
#             datum2 = _ref5[_k]
#             parseDate = d3.time.format("%Y-%m-%dT%H:%M:%S").parse
#             if time is "date"
#                 try
#                     start2 = Date.parse(@data.models[_k].attributes.data.Time)
#                 catch err
#                     start2 = null
#             else
#                 start2 = parseDate(@data.models[_k].get("timestamp"))
#             d2 = Math.floor(start2 / secs)
#             geopoint = datum2.get("data")[@map_headers].split(" ")
#             if val >= Math.abs(d - d2)
#                 @pL.push [parseFloat(geopoint[0]), parseFloat(geopoint[1])]
#                 @poly = L.polyline(@pL, @pLStyle).addTo(@map)
#             else
#                 break
#             _k++
#         _j++
