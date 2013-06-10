import json
import urllib

from backend.db import user_or_organization

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.core.files.storage import default_storage as storage

from lxml import etree
from repos import validate_and_format
from repos.models import Repository


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


def _parse_xml_submission( xml_data, root, files ):
    for element in root:

        if element.text in files:
            xml_data[ element.tag ] = files.get( element.text )
        else:
            xml_data[ element.tag ] = element.text

        if element.getchildren() > 0:
            _parse_xml_submission( xml_data, element, files )


@csrf_exempt
@require_POST
def xml_submission( request, username ):

    root = etree.fromstring(request.FILES[ 'xml_submission_file' ].read())

    # Find the user object associated with this username
    account = user_or_organization( username )

    # The find the repo object associated with this form name & user
    repo_name = root.tag
    repo = Repository.objects.get_by_username( repo_name, username )

    # Parse the xml data
    xml_data = {}
    _parse_xml_submission( xml_data, root, request.FILES )

    # Do basic validation of the data
    new_data = repo.add_data( xml_data, request.FILES )

    return HttpResponse( json.dumps( { 'success': True } ),
                         mimetype='application/json' )
