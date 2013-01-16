'''
    serializer.py

    Functions and helpers to handle OpenROSA API support.
'''
import json
import StringIO

from backend.db import db
from bson import ObjectId

from django.shortcuts import render_to_response

from tastypie.serializers import Serializer

from pyxform.builder import create_survey_element_from_dict
from pyxform.xls2json import SurveyReader


class XFormSerializer( Serializer ):
    '''
        Uses the pyxform provided classes to convert from JSON -> XForm xml
        and back again.
    '''
    formats = [ 'xform', 'json', 'html' ]
    content_types = {
        'html': 'text/html',
        'json': 'application/json',
        'xform': 'application/xml',
    }

    def to_html( self, data, options=None ):
        '''
            Direct user to an HTML version of the form
        '''
        options = options or {}
        data    = self.to_simple( data, options )
        return render_to_response( 'forms/get.html', {'form': data} )

    def to_xform( self, data, options=None ):
        options = options or {}
        data    = self.to_simple( data, options )

        # We only want to return the special xform format when there is an
        # survey id present.
        if 'id' not in data:
            return self.to_xml( data )

        # Grab the form & convert into the xform format!
        survey_data = db[ 'survey' ].find_one(
                            {'_id': ObjectId( data[ 'id' ] ) } )
        survey  = create_survey_element_from_dict( survey_data )

        return survey._to_pretty_xml()

    def from_xform( self, content ):
        raw_data = StringIO.StringIO( content )
        survey = SurveyReader( raw_data )

        return survey.to_json_dict()
