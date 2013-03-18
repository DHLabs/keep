$ ->
	$.getJSON( '/api/v1/data/', { 'user': $( '#user' ).html() }, ( data ) ->

		console.log( moment().format() );

		$( '#submissions_feed' ).html( '' );

		if data.length == 0
			$( '#submissions_feed' ).html( '<div style="color:#AAA;">No submissions yet =[</div>' )
		else

			feed_tmpl = _.template( $( '#submission_feed_tmpl' ).html() )

			for datum in data

				info =
					label: 'submission received'
					time: moment.utc( datum.timestamp ).fromNow()
					link: "/api/v1/data/#{ datum.survey }"

				$( '#submissions_feed' ).append( feed_tmpl( info ) )
	)
