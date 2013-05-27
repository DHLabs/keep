import json
import urllib

from backend.db import Repository, user_or_organization

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.core.files.storage import default_storage as storage

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

    kwargs = {}
    if 'iphone_id' in request.POST:
        kwargs = { 'uuid': request.POST[ 'iphone_id' ] }

    new_data = Repository.add_data( repo, valid_data, account, **kwargs )

    if len( request.FILES.keys() ) > 1:

        # If we have media data, save it to this repo's data folder
        storage.bucket_name = 'keep-media'

        for key in request.FILES.keys():
            # Ignore the XML file
            if key == 'xml_submission_file':
                continue

            # S3 URL consistes of the repo ID, the ID associated with this row
            # of data, and then the filename.
            #
            # TODO: Queue up file for download rather than uploading directly
            # to S3.
            s3_url = '%s/%s/%s' % ( repo[ '_id' ], new_data, key )
            storage.save( s3_url, request.FILES[ key ] )

    return HttpResponse( json.dumps( { 'success': True } ),
                         mimetype='application/json' )
