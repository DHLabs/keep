# Requirejs will inline common dependencies into this file.

requirejs.config(
	baseUrl: 'js/vendor'
	paths:
		app: '../app'

		# Leaflet plugins
		leaflet_heatmap: 'heatmap-leaflet'
		leaflet_cluster: 'leaflet.markercluster'

		# jQuery plugins
		jqueryui: 'jquery-ui'
		jquery_cookie: 'jquery.cookie'

		# Backbone plugins
		backbone_modal: 'backbone.modal'
		marionette: 'backbone.marionette'

		nvd3: 'nv.d3'

	shim:
		jqueryui:
			deps: [ 'jquery' ]

		jquery_cookie:
			deps: [ 'jquery' ]

		# Backbone & associated plugins
		backbone:
			deps: [ 'jquery', 'underscore' ]
			exports: 'Backbone'

		underscore:
			exports: '_'

		backbone_modal:
			deps: [ 'backbone' ]

		marionette:
			deps: [ 'jquery', 'underscore', 'backbone' ]
			exports: 'Marionette'

		'd3':
			exports: 'd3'

		'nvd3':
			deps: [ 'd3' ]
			exports: 'nv'

		# Leaflet & associated plugins
		leaflet_heatmap:
			deps: [ 'leaflet', 'heatmap' ]
		leaflet_cluster:
			deps: [ 'leaflet' ]
)
