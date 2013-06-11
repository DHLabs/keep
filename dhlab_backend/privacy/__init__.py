import math
from numpy import linspace

from .map import privatize


def privatize_geo( repo, data ):
    # Does this data have any geo data?
    has_geo = False
    geo_index = None
    for field in repo[ 'children' ]:
        if field[ 'type' ] == 'geopoint':
            has_geo = True
            geo_index = field[ 'name' ]
            break

    # Great! We have geopoints, let's privatize this data
    if has_geo:
        xbounds     = [ None, None ]
        ybounds     = [ None, None ]
        fuzzed_data = []

        for datum in data:

            geopoint = datum[ 'data' ][ geo_index ].split( ' ' )

            try:
                point = ( float( geopoint[0] ), float( geopoint[1] ) )
            except ValueError:
                continue

            if xbounds[0] is None or point[0] < xbounds[0]:
                xbounds[0] = point[0]

            if xbounds[1] is None or point[0] > xbounds[1]:
                xbounds[1] = point[0]

            if ybounds[0] is None or point[1] < ybounds[0]:
                ybounds[0] = point[1]

            if ybounds[1] is None or point[1] > ybounds[1]:
                ybounds[1] = point[1]

            fuzzed_data.append( point )

        # Split the xbounds in a linear
        num_x_samples = int(math.ceil( ( xbounds[1] - xbounds[0] ) / .2 ))
        num_y_samples = int(math.ceil( ( ybounds[1] - ybounds[0] ) / .2 ))

        xbounds = linspace( xbounds[0], xbounds[1], num=num_x_samples )
        ybounds = linspace( ybounds[0], ybounds[1], num=num_y_samples )

        fuzzed_data = privatize( points=fuzzed_data,
                                 xbounds=xbounds,
                                 ybounds=ybounds )
        data = []
        for datum in fuzzed_data:
            data.append( {
                'data':
                {geo_index: ' '.join( [ str( x ) for x in datum ] )}})

    return data
