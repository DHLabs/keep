from django.test import TestCase

from openrosa.xform_reader import XFormReader

# Tutorial xform with basic data/survey types
XFORM_FILE              = '../_data/test_docs/tutorial.xml'
# Basic i18n xform with translated labels
I18N_XFORM              = '../_data/test_docs/zambia/Child Visit.xml'
# Translated constraint messages.
I18N_CONSTRAINTS_XFORM  = '../_data/test_docs/zambia/Delivery.xml'


class XFORMReaderTests( TestCase ):

    def test_read_basic_xform( self ):
        '''
            Attempt to read the basic tutorial xform which contains all the basic
            data and survey types.
        '''
        reader = XFormReader( XFORM_FILE )
        json = reader.to_json_dict()

        assert json is not None
        assert json.get( 'type' ) == 'survey'

    def test_read_i18n_xform( self ):
        '''
            Attempt to read a more advanced xform which contains translations
            for labels.
        '''
        reader = XFormReader( I18N_XFORM )
        json = reader.to_json_dict()

        assert json is not None
        assert json.get( 'type' ) == 'survey'

        reader = XFormReader( I18N_CONSTRAINTS_XFORM )
        json = reader.to_json_dict()

        assert json is not None
        assert json.get( 'type' ) == 'survey'
