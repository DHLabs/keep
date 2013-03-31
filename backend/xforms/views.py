import json

from backend.db import db, encrypt_survey
from backend.xforms import validate_and_format

from datetime import datetime

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

from lxml import etree


@csrf_exempt
def xml_submission( request, username ):
    if request.method == 'POST':
        iphone_id = request.GET.get( 'iphone_id', None )

        root = etree.fromstring(request.FILES[ 'xml_submission_file' ].read())

        # Find the user object associated with this username
        user = User.objects.get(username=username)

        # The find the suervey object associated with this form name & user
        survey_name = root.tag
        survey = db.survey.find_one( { 'name': survey_name, 'user': user.id } )

        # Parse the xml data
        xml_data = {}
        for element in root:
            xml_data[ element.tag ] = element.text

        # Do basic validation of the data
        valid_data = validate_and_format( survey, xml_data )

        # Include some metadata with the survey data
        survey_data = {
            # User ID of the person who uploaded the form (not the data)
            'user':         user.id,
            # Survey/form ID associated with this data
            'survey':       survey[ '_id' ],

            # Survey name (used for feed purposes)
            'survey_label': survey[ 'name' ],

            # Timestamp of when this submission was received
            'timestamp':    datetime.utcnow(),
            # The validated & formatted survey data.
            'data':         encrypt_survey( valid_data )
        }

        # Save the iphone_id ( if passed in by the submitter )
        if iphone_id:
            survey_data[ 'uuid' ] = iphone_id

        # Insert into the database
        db.survey_data.insert( survey_data )

        data = json.dumps( { 'success': True } )
        return HttpResponse( data, mimetype='application/json' )

    return HttpResponseNotAllowed( ['POST'] )
