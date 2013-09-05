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
                <% _.each( fields, function( field ) { %>
                    <div><%= field.name %>: <%= model.data[ field.name ] %></div>
                <% }); %><td>&nbsp;</td>''')

            return templ( data )


    class DataMapView extends Backbone.Marionette.CollectionView
        el: '#map-viz'
        itemView: MarkerItemView

        _detect_headers: ( fields ) ->
            @map_headers = []

            for field in fields
                if field.type in [ 'geopoint' ]
                    @map_headers.push( field )

        _resize_map: () =>
            $( '#map' ).css( { 'height': @$el.parent().height() + 'px' } )
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
            @map = L.map( 'map' ).setView( [ 0, 0 ], 10 )
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
            # Instead of appending these views into the DOM, place them in the
            # map instead!
            point = itemView.model.geopoint( collectionView.map_headers[0] )
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
            # Everytime we move around, grab new data from the server and
            # refresh the viewport!
            bounds = event.target.getBounds()
            @collection.fetch(
                reset: true
                data:
                    bbox: bounds.toBBoxString() )

            @

    return DataMapView
)