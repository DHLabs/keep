from tests import ApiTestCase


class OpenRosaAPITests( ApiTestCase ):

    def test_formlist( self ):
        '''
        '''
        response = self.openRaw( '/bs/admin/formList', None )
        assert response is not None

    def test_repo_xform_xml( self ):
        '''
            Test if we can list the repo details for a specific repo for a
            test user.
        '''

        # Get the list of repos for the test user
        response = self.open( '/repos/', {'format': 'json', 'user': 'admin'} )
        repo = response[ 'objects' ][0][ 'id' ]

        # Grab the repo details
        response = self.open( '/repos/%s' % ( repo ),
                              {'format': 'xform', 'user': 'admin'},
                              format='xform' )

        assert response is not None
