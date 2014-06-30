# dashboard/main.coffee
#
# Dashboard/main.coffee represents the view(s) rendered when a user accesses
# their personal dashboard or some other user's dashboard.
#
# The dashboard shows a list of the user's data repos and various stats for each
# repo.
#

define( [ 'require' ],
( require ) ->

	require( [ 'app/dashboard/views' ],
		( DashboardView ) ->
			document.dashboardApp = new DashboardView();
	)

)