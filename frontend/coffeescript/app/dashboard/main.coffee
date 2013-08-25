define( [ 'require' ],
( require ) ->

	require( [ 'app/dashboard/views' ],
		( DashboardView ) ->
			document.dashboardApp = new DashboardView();
	)

)