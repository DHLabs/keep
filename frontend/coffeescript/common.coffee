# Requirejs will inline common dependencies into this file.

requirejs.config(
	baseUrl: 'js/vendor'
	paths:
		app: '../app'

		leaflet_heatmap: 'heatmap-leaflet'
		leaflet_cluster: 'leaflet.markerclusterer'

		dataTables: 'jquery.dataTables.min'
		bootstrapTables: 'bootstrap.dataTables'

	shim:
		backbone:
			deps: [ 'jquery', 'underscore' ]
			exports: 'Backbone'
		underscore:
			exports: '_'

		# Leaflet & associated plugins
		leaflet:
			deps: [ 'jquery' ]
			exports: 'L'
		leaflet_heatmap:
			deps: [ 'leaflet', 'heatmap' ]
		leaflet_cluster:
			deps: [ 'leaflet' ]

		# jQuery DataTables & associated plugins
		dataTables:
			deps: [ 'jquery' ]
		bootstrapTables:
			deps: [ 'dataTables' ]

		# Form editing stuff
		'forms/editors/list':
			deps: [ 'backbone', 'backbone-forms' ]

		'forms/templates/bootstrap':
			deps: [ 'backbone', 'backbone-forms', 'forms/editors/list' ]

)
