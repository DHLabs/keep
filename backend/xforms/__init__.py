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
