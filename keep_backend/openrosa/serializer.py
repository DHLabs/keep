'''
    serializer.py

    Functions and helpers to handle OpenROSA API support.
'''
from django.conf import settings

from lxml import etree

from tastypie.serializers import Serializer

from pyxform.builder import create_survey_element_from_dict

from json_xls_convert import jsonXlsConvert


class XFormSerializer( Serializer ):
    '''
        Uses the pyxform provided classes to convert from JSON -> XForm xml
        and back again.
    '''
    formats = [ 'xform', 'json', 'xls' ]
    content_types = {
        'json': 'application/json',
        'xform': 'text/xml',
        'xls': 'application/vnd.ms-excel'
    }

    def to_formList( self, repos ):
        root = etree.Element( 'xforms' )
        root.set( 'xmlns', 'http://openrosa.org/xforms/xformsList' )

        for xform in repos:

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

            downloadUrl = etree.Element( 'downloadUrl' )

            if settings.DEBUG:
                base_url = 'http://%s/api/v1/repos/' % ('localhost:8000')
            else:
                base_url = 'http://%s/api/v1/repos/' % (settings.HOSTNAME)

            downloadUrl.text = '%s%s/?format=xform' % ( base_url, xform[ 'id' ] )

            element.append( downloadUrl )

            manifestUrl = etree.Element( 'manifestUrl' )
            manifestUrl.text = '%s%s/manifest/?format=xml' % ( base_url, xform[ 'id' ] )

            element.append( manifestUrl )
            element.append( etree.Element( 'descriptionText' ) )

            root.append( element )

        return etree.tostring( root )

    def to_manifest( self, data ):
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

    def to_xform( self, data, options=None ):
        options = options or {}
        data    = self.to_simple( data, options )

        if 'manifest' in data:
            # Return the xform manifest
            return self.to_manifest( data )
        elif 'objects' in data:
            # Return the formList representation of our objects if they are
            # present.
            return self.to_formList( data.get( 'objects', [] ) )
        elif 'id' in data:
            # Accessing a single repo object! Convert completely into the
            # xform format.
            xform = {}
            xform[ 'name' ] = data.get( 'name' )
            # TODO: Fix pyxform to handle this correctly. #  data.get( 'type' )
            xform[ 'type' ] = 'survey'
            xform[ 'default_language' ] = data.get( 'default_language', 'default' )
            xform[ 'children' ] = data.get( 'children' )

            return create_survey_element_from_dict( xform )._to_pretty_xml()
        else:
            raise Exception( data )

        return None

    def to_xls( self, data, options=None ):
        options = options or {}
        data    = self.to_simple(data, options)
        converter = jsonXlsConvert(data.get('name'))

        return converter.writeToXls(data.get("children"))
