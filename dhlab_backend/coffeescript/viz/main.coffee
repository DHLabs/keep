requirejs.config
	paths:
		vendor: '/static/js/vendor'
		dataTables: '/static/js/vendor/datatables/jquery.dataTables.min'
		bootstrapTables: '/static/js/vendor/datatables/bootstrap.dataTables'

		masonry: '/static/js/vendor/masonry/masonry'

		leaflet: '/static/js/vendor/leaflet/leaflet'
		heatmap: '/static/js/vendor/leaflet/heatmap'
		leaflet_heatmap: '/static/js/vendor/leaflet/heatmap-leaflet'
		leaflet_cluster: '/static/js/vendor/leaflet/leaflet.markercluster'

	shim:
		'vendor/underscore':
			exports: '_'
		'vendor/backbone-min':
			deps: [ 'vendor/underscore', 'jquery' ]
			exports: 'Backbone'
		'dataTables':
			deps: [ 'jquery' ]
		'bootstrapTables':
			deps: [ 'dataTables' ]
		'masonry':
			exports: 'Masonry'
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