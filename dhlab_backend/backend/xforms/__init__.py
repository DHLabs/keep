import urllib

from django.core.urlresolvers import reverse
from django.shortcuts import redirect


def formlist( request, username ):
    api_url = reverse( 'api_dispatch_list',
                    kwargs={'resource_name': 'forms',
                            'api_name': 'v1'} )

    key     = request.GET.get( 'key', None )
    format  = request.GET.get( 'format', 'xform' )

    api_url = '%s?%s' % ( api_url, urllib.urlencode({
            'user': username,
            'key': key,
            'format': format
        }) )

    return redirect( api_url )


def submission_detail( request ):
    pass


def validate_and_format( form, data ):
    '''
        Do some basic validation and convert strings to <type> where
        necessary.
    '''

    survey_data = {}
    for element in form[ 'children' ]:

        etype = element[ 'type' ]
        ename = element[ 'name' ]

        # Do type conversions
        if ename in data:

            # Convert to integer
            if etype is 'integer':
                survey_data[ ename ] = int( data[ ename ] )
            else:
                survey_data[ ename ] = data[ ename ]

    return survey_data
