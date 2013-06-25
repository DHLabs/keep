define( [ 'require' ],
( require ) ->

	require( [ 'app/viz/views', 'dataTables', 'bootstrapTables' ],
		( DataView ) ->
			document.vizApp = new DataView();
	)

)