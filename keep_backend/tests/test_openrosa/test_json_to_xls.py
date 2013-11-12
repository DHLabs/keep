from django.test import TestCase

from openrosa.xform_reader import XFormReader
from openrosa.json_xls_convert import jsonXlsConvert

# Tutorial xform with basic data/survey types
XFORM_FILE              = '../_data/test_docs/tutorial.xml'


class JSONToXLSTests( TestCase ):

    def test_conversion( self ):
        reader = XFormReader( XFORM_FILE )
        json = reader.to_json_dict()

        converter = jsonXlsConvert( '/tmp/test.xls' )
        converter.writeToXls( json.get( 'children' ) )
