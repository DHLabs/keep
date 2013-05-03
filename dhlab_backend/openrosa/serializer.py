'''
    serializer.py

    Functions and helpers to handle OpenROSA API support.
'''
import StringIO

from backend.db import db
from bson import ObjectId
from django.conf import settings

from lxml import etree

from tastypie.serializers import Serializer

from pyxform.builder import create_survey_element_from_dict
from pyxform.xls2json import SurveyReader


class XFormSerializer( Serializer ):
    '''
        Uses the pyxform provided classes to convert from JSON -> XForm xml
        and back again.
    '''
    formats = [ 'xform', 'json' ]
    content_types = {
        'json': 'application/json',
        'xform': 'text/xml',
    }

    def to_xform( self, data, options=None ):
        options = options or {}
        data    = self.to_simple( data, options )

        # We only want to return the special xform format when there is an
        # survey id present.
        if 'id' not in data and 'objects' in data:
            root = etree.Element( 'xforms' )
            root.set( 'xmlns', 'http://openrosa.org/xforms/xformsList' )

            for xform in data[ 'objects' ]:
                element = etree.Element( 'xform' )

                formId = etree.Element( 'formID' )
                formId.text = xform[ 'title' ]
                element.append( formId )

                name = etree.Element( 'name' )
                name.text = xform[ 'name' ]
                element.append( name )

                downloadUrl = etree.Element( 'downloadUrl' )

                if settings.DEBUG:
                    base_url = 'localhost:8000'
                else:
                    base_url = 'keep.distributedhealth.org'

                downloadUrl.text = 'https://%s/api/v1/repos/%s/?format=xform&user=%s' %\
                                   ( base_url, xform[ 'id' ], xform[ 'owner'] )

                element.append( downloadUrl )

                element.append( etree.Element( 'descriptionText' ) )
                element.append( etree.Element( 'manifestUrl' ) )

                root.append( element )

            return etree.tostring( root )
        elif 'id' not in data:
            return self.to_xml( data )

        # Grab the form & convert into the xform format!
        survey_data = db[ 'survey' ].find_one({'_id': ObjectId( data['id'])})
        survey  = create_survey_element_from_dict( survey_data )

        return survey._to_pretty_xml()

    def from_xform( self, content ):
        raw_data = StringIO.StringIO( content )
        survey = SurveyReader( raw_data )

        return survey.to_json_dict()
