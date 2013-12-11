# Requirejs will inline common dependencies into this file.

requirejs.config(
	baseUrl: 'js/vendor'
	paths:
		app: '../app'

		# Leaflet plugins
		leaflet_heatmap: 'heatmap-leaflet'
		leaflet_cluster: 'leaflet.markerclusterer'

		# jQuery plugins
		jqueryui: 'jquery-ui'
		jquery_cookie: 'jquery.cookie'

		# Backbone plugins
		backbone_modal: 'backbone.modal'
		marionette: 'marionette'

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

		# Leaflet & associated plugins
		leaflet_heatmap:
			deps: [ 'leaflet', 'heatmap' ]
		leaflet_cluster:
			deps: [ 'leaflet' ]

		# Form editing stuff
		'forms/editors/list':
			deps: [ 'backbone', 'backbone-forms' ]

		'forms/templates/bootstrap':
			deps: [ 'backbone', 'backbone-forms', 'forms/editors/list' ]

)
