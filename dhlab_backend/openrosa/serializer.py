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

        if 'manifest' in data:

            root = etree.Element( 'manifest' )
            root.set( 'xmlns', 'http://openrosa.org/xforms/xformsManifest' )

            for media in data[ 'manifest' ]:
                mediaFile = etree.Element( 'mediaFile' )

                fileName = etree.Element( 'filename' )
                fileName.text = media

                downloadUrl = etree.Element( 'downloadUrl' )
                downloadUrl.text = 'http://s3.amazonaws.com/keep-media/%s/%s' % ( data[ 'repo' ], media )

                mediaFile.append( fileName )
                mediaFile.append( downloadUrl )

                root.append( mediaFile )

            return etree.tostring( root )

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

                owner = xform['user'] if 'user' in xform else xform[ 'org' ]

                downloadUrl = etree.Element( 'downloadUrl' )

                base_url = 'http://%s/api/v1/repos/'
                if settings.DEBUG:
                    base_url = base_url % ( 'localhost:8000' )
                else:
                    base_url = base_url % ( 'keep.distributedhealth.org' )

                downloadUrl.text = '%s%s/?format=xform&user=%s' %\
                                   ( base_url, xform[ 'id' ], owner )

                element.append( downloadUrl )

                manifestUrl = etree.Element( 'manifestUrl' )
                manifestUrl.text = '%s%s/manifest/?format=xml&user=%s' %\
                                   ( base_url, xform[ 'id' ], owner )

                element.append( manifestUrl )
                element.append( etree.Element( 'descriptionText' ) )

                root.append( element )

            return etree.tostring( root )
        elif 'id' not in data:
            print data
            return self.to_xml( data )

        # Grab the form & convert into the xform format!
        survey_data = db[ 'survey' ].find_one({'_id': ObjectId( data['id'])})
        survey  = create_survey_element_from_dict( survey_data )

        return survey._to_pretty_xml()
