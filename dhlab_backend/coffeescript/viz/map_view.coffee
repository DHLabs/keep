define( [ 'jquery',
          'vendor/underscore',
          'vendor/backbone-min',
          'leaflet',
          'leaflet_heatmap',
          'leaflet_cluster' ],

( $, _, Backbone, L ) ->

    class MapView extends Backbone.View

        name: "MapView"
        el: $( '#map' )

        initialize: ( options ) ->
            @parent = options.parent
            @data   = options.data
            @map_headers = options.map_headers

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

                geopoint = datum.get( 'data' )[ @map_headers ]
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

            @map = L.map('map').setView( center, 10 )
            @test_map = L.map( 'hidden_map' ).setView( center, 10 );

            L.tileLayer( 'http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
                            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
                            maxZoom: 18 }).addTo( @map )

            myIcon = L.icon(
                        iconUrl: '//keep-static.s3.amazonaws.com/img/leaflet/marker-icon.png'
                        iconRetinaUrl: '//keep-static.s3.amazonaws.com/img/leaflet/marker-icon@2x.png'
                        iconSize: [25, 41]
                        iconAnchor: [12, 41]
                        popupAnchor: [1, -34]
                        shadowUrl: '//keep-static.s3.amazonaws.com/img/leaflet/marker-shadow.png'
                        shadowSize: [41, 41]
                        shadowAnchor: [15, 41] )

            heatmapData = []
            @markers = []
            @constrained_markers = []
            @marker_layer = new L.MarkerClusterGroup()
            for datum in @data.models
                geopoint = datum.get( 'data' )[ @map_headers ].split( ' ' )

                if isNaN( geopoint[0] ) or isNaN( geopoint[1] )
                    continue

                marker = L.marker( [geopoint[0], geopoint[1]], {icon: myIcon})

                html = ''
                for key, value of datum.get( 'data' )
                    html += "<div><strong>#{key}:</strong> #{value}</div>"
                marker.bindPopup( html )

                @marker_layer.addLayer( marker )
                constrainedMarker = L.marker( [geopoint[0], geopoint[1]], {icon: myIcon})

                heatmapData.push(
                    lat: geopoint[0]
                    lon: geopoint[1]
                    value: 1 )

            @constrained_layer = L.layerGroup( @constrained_markers )
            @heatmap.addData( heatmapData )
            @map.addLayer( @heatmap )
            @map.addLayer( @marker_layer )

            layers =
                'Markers': @marker_layer
                'Heatmap': @heatmap

            controls = L.control.layers( null, layers, { collapsed: false } )
            controls.addTo( @map )
            @

    return MapView
)