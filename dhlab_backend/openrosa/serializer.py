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
                fileName.text = media[0]

                downloadUrl = etree.Element( 'downloadUrl' )
                downloadUrl.text = media[1]

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
                formId.text = xform[ 'name' ]
                element.append( formId )

                name = etree.Element( 'name' )
                name.text = xform[ 'name' ]
                element.append( name )

                formType = etree.Element( 'type' )
                formType.text = xform[ 'type' ]
                element.append( formType )

                owner = xform['user']

                downloadUrl = etree.Element( 'downloadUrl' )

                if settings.DEBUG:
                    base_url = 'http://%s/api/v1/repos/' % ('localhost:8000')
                else:
                    base_url = 'http://%s/api/v1/repos/' % (settings.HOSTNAME)

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
            raise Exception( data )

        # Grab the form & convert into the xform format!
        xform = {
            'name': data[ 'name' ],
            'type': 'survey',
            'default_language': 'default' }
        xform[ 'children' ] = db.repo.find_one( ObjectId( data[ 'id' ] ) )[ 'fields' ]
        survey  = create_survey_element_from_dict( xform )
        return survey._to_pretty_xml()
