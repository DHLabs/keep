from django.test import TestCase

from openrosa.serializer import XFormSerializer
from openrosa.xform_reader import XFormReader
from repos.models import Repository, RepoSerializer

# Tutorial xform with basic data/survey types
XFORM_FILE    = '../_data/test_docs/tutorial.xml'

MANIFEST_DATA = { 'repo': 'test_repo',
                  'manifest': [ ( 'media_name', 'media_url' ) ] }


class OpenRosaSerializerTests( TestCase ):

    fixtures = [ '../_data/fixtures/test_data.yaml' ]

    def setUp( self ):
        reader = XFormReader( XFORM_FILE )

        self.data = reader.to_json_dict()
        self.data[ 'name' ] = 'test_repo'

        serializer = RepoSerializer()
        self.repos = serializer.serialize( Repository.objects.all() )

    def test_to_formList( self ):
        '''
            Test the conversion from a list of repos to a OpenRosa "formList"
            specification.
        '''
        serializer = XFormSerializer()
        result = serializer.to_formList( self.repos )

        assert result is not None
        return result

    def test_to_manifest( self ):
        '''
            Test the conversion from dictionary to manifest.
        '''
        serializer = XFormSerializer()
        result = serializer.to_manifest( MANIFEST_DATA )

        assert result is not None
        return result

    def test_to_xform( self ):
        '''
            Test the generic xform serializer. The serializer should be able to
            detect what data type it's looking at and appropriately convert it
            to XML.
        '''
        serializer = XFormSerializer()
        objects = { 'objects': self.repos }

        assert serializer.to_xform( objects ) == self.test_to_formList()
        assert serializer.to_xform( MANIFEST_DATA ) == self.test_to_manifest()
        assert serializer.to_xform( self.repos[0] ) is not None

        exception_thrown = False
        try:
            serializer.to_xform( {} )
        except Exception as e:
            exception_thrown = True

        assert exception_thrown is True

    def test_to_xls( self ):
        '''
            Test the serializer's conversion from JSON -> XLS.
        '''
        serializer = XFormSerializer()
        assert serializer.to_xls( self.data ) is not None
