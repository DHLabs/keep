import json
import urllib

from backend.db import Repository, user_or_organization

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from lxml import etree
from repos import validate_and_format


def formlist( request, username ):
    api_url = reverse( 'api_dispatch_list',
                       kwargs={'resource_name': 'repos',
                               'api_name': 'v1'} )

    key     = request.GET.get( 'key', None )
    format  = request.GET.get( 'format', 'xform' )

    api_url = '%s?%s' % ( api_url, urllib.urlencode({
                         'user': username,
                         'key': key,
                         'format': format }) )

    return redirect( api_url )


def submission_detail( request ):
    pass


def _parse_xml_submission( xml_data, root ):
    for element in root:
        xml_data[ element.tag ] = element.text

        if element.getchildren() > 0:
            _parse_xml_submission( xml_data, element )


@csrf_exempt
@require_POST
def xml_submission( request, username ):
    iphone_id = request.POST.get( 'iphone_id', None )

    root = etree.fromstring(request.FILES[ 'xml_submission_file' ].read())

    # Find the user object associated with this username
    account = user_or_organization( username )

    # The find the suervey object associated with this form name & user
    repo_name = root.tag
    repo = Repository.get_repo( repo_name, account )

    # Parse the xml data
    xml_data = {}
    _parse_xml_submission( xml_data, root )

    # Do basic validation of the data
    valid_data = validate_and_format( repo, xml_data )

    if iphone_id:
        Repository.add_data( repo, valid_data, account, uuid=iphone_id )
    else:
        Repository.add_data( repo, valid_data, account, uuid=iphone_id )

    data = json.dumps( { 'success': True } )
    return HttpResponse( data, mimetype='application/json' )
