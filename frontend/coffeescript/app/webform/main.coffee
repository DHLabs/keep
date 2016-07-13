define( [ 'require' ],
( require ) ->

	require( [ 'app/webform/views' ],
		( xFormView ) ->
			app = new xFormView()
	)

)
