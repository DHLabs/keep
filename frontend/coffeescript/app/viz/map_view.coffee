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

        # Find a column that can be plotted on the map.
        # TODO: Support lat/lngs as separate columns.
        _detect_headers: ( fields ) ->
            @map_headers = []
            @selected_header = null

            for field in fields when field.type is 'geopoint'
                @selected_header or= field

        # Add a geopoint to all of the map layers.
        _add_to_layers: (datum, geopoint) ->

          # Set up a pop-up so that when the marker is clicked, the fields for
          # that data point are showed.
          fields =
            for key, value of datum.get( 'data' )
              "<div><strong>#{key}:</strong> #{value}</div>"
          marker = L.marker( [geopoint.lat, geopoint.lng], {icon: mapIcon} )
          marker.bindPopup( fields.join('') )

          @markers.addLayer( marker )
          @clusters.addLayer( marker )
          @heatmap.addDataPoint( {'lon': geopoint.lng, 'lat': geopoint.lat, 'value': 1 } )

        _geopoint: ( datum ) ->
            # Ensure there is a column with geopoint data
            return null if not @selected_header?.name?

            # Get geopoint data
            geopoint = datum.get('data')[ @selected_header.name ]
            return null if not geopoint?

            # Get Lat/Lng
            [lat, lng] = [geopoint.coordinates[1],geopoint.coordinates[0]]
            lat = parseFloat(lat)
            lng = parseFloat(lng)
            return null if isNaN(lat) or isNaN(lng)

            # Bound latitude from -90 to 90
            lat = lat - 180 while lat > 90
            lat = lat + 180 while lat < -90

            # Bound longitude from -180 to 180
            lng = lng - 360 while lng > 180
            lng = lng + 360 while lng < -180

            return { lat: lat, lng: lng }

        render: ->
          for datum in @collection.models
            geopoint = @_geopoint( datum )
            continue if not geopoint?
            @_add_to_layers(datum, geopoint)

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

            # Enable markers by default
            @map.addLayer @markers

            @controls = L.control.layers( null, layers, { collapsed: false } )
            @controls.addTo( @map )

            @data_offset = 0

            # Listen to events
            @map.on( 'moveend', @refresh_viewport )

            # Clear all our markers when we get another set of markers.
            @collection.on( 'reset', =>
                @markers.clearLayers()
                @clusters.clearLayers() )
            @

        # We aren't appending HTML to the DOM in the standard way; rather than
        # appending HTML to the collections el, we want to render each
        # geopoint on our Leaflet map.
        appendHtml: (collectionView, itemView, index) ->

            # If we could not find any geofields or the user has not specified
            # an existing one, don't do anything with the data.
            return if not collectionView.selected_header?
            point = @_geopoint(itemView.model)
            return if not point?

            # Instead of appending these views into the DOM, place them in the
            # map instead!
            @_add_to_layers(itemView.model, point)

        buildItemView: ( item, ItemViewType, itemViewOptions ) ->
            options = _.extend( { model: item, fields: @fields }, itemViewOptions )
            return new ItemViewType( options )

        onShow: =>
          # For some reason map.getSize() is cached and returns 0, so
          # invalidateSize() doesn't work.
          @map._onResize()

        get_next_page: ->
          @data_offset = @data_offset + 1

          @collection.fetch
            reset: false
            data:
              geofield: @selected_header.name
              bbox: @bounds.toBBoxString()
              offset: @data_offset
            success: (collection, response, options) =>
              @get_next_page() if response.meta.pages > @data_offset

        # Everytime we move around, grab new data from the server and
        # refresh the viewport!
        refresh_viewport: ( event ) =>
          # If we could not find any geofields or the user has not
          # specified an existing one, don't do anything with the
          # data.
          return if not @selected_header?

          @data_offset = 0
          @bounds = event.target.getBounds()

          @collection.fetch
            reset: true
            data:
              geofield: @selected_header.name
              bbox: @bounds.toBBoxString()
            success: (collection, response, options) =>
              @get_next_page() if response.meta.pages > 0

    return DataMapView
)
