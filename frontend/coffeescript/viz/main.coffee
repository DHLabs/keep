requirejs.config
	paths:
		vendor: document.cdn + 'js/vendor'
		dataTables: document.cdn + 'js/vendor/datatables/jquery.dataTables.min'
		bootstrapTables: document.cdn + 'js/vendor/datatables/bootstrap.dataTables'

		masonry: document.cdn + 'js/vendor/masonry/jquery.masonry'

		leaflet: document.cdn + 'js/vendor/leaflet/leaflet'
		heatmap: document.cdn + 'js/vendor/leaflet/heatmap'
		leaflet_heatmap: document.cdn + 'js/vendor/leaflet/heatmap-leaflet'
		leaflet_cluster: document.cdn + 'js/vendor/leaflet/leaflet.markercluster'

		views: document.cdn + 'js/viz/views'

	shim:
		# Backbone
		'vendor/underscore':
			exports: '_'
		'vendor/backbone-min':
			deps: [ 'vendor/underscore', 'jquery' ]
			exports: 'Backbone'

		# jQuery DataTables & associated plugins
		'dataTables':
			deps: [ 'jquery' ]
		'bootstrapTables':
			deps: [ 'dataTables' ]

		# Masonry
		'masonry':
			deps: [ 'jquery' ]

		# Leaflet & associated plugins
		'leaflet':
			deps: [ 'jquery' ]
			exports: 'L'
		'leaflet_heatmap':
			deps: [ 'leaflet', 'heatmap' ]
		'leaflet_cluster':
			deps: [ 'leaflet' ]

require( [ 'views', 'dataTables', 'bootstrapTables' ],

	( DataView ) ->
		document.vizApp = new DataView();
)