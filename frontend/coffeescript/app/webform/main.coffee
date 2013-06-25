define( [ 'require' ],
( require ) ->

	require( [ 'app/webform/views', 'forms/templates/bootstrap' ],
		( xFormView ) ->
			app = new xFormView()
	)

)