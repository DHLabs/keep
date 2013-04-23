requirejs.config
	paths:
		vendor: '/static/js/vendor'
	shim:
		'vendor/underscore':
			exports: '_'
		'vendor/backbone-min':
			deps: [ 'vendor/underscore', 'jquery' ]
			exports: 'Backbone'
		'vendor/forms/editors/list':
			deps: [ 'vendor/backbone-min', 'vendor/forms/backbone-forms.min' ]
		'vendor/forms/templates/bootstrap':
			deps: [ 'vendor/backbone-min', 'vendor/forms/backbone-forms.min',
					'vendor/forms/editors/list' ]

require( [ 'views', 'vendor/forms/templates/bootstrap' ],
	( xFormView ) ->

		app = new xFormView()
)