import json

from tests import ApiTestCase


class OpenRosaAPITests( ApiTestCase ):

    AUTH_DETAILS = { 'format':  'json',
                     'user':    'admin',
                     'key':     '35f7d1fb1890bdc05f9988d01cf1dcab' }

    AUTH_DETAILS_XFORM = { 'format':  'xform',
                           'user':    'admin',
                           'key':     '35f7d1fb1890bdc05f9988d01cf1dcab' }

    def test_formlist( self ):
        '''
        '''
        response = self.client.get( '/bs/admin/formList', self.AUTH_DETAILS_XFORM, follow=True )
        assert response.status_code == 200

    def test_repo_xform_xml( self ):
        '''
            Test if we can list the repo details for a specific repo for a
            test user.
        '''

        # Get the list of repos for the test user
        response = self.open( '/repos/', self.AUTH_DETAILS )
        response = json.loads( response.content )

        for repo in response.get( 'objects' ):
            response = self.open( '/repos/%s/' % ( repo.get( 'id' ) ), self.AUTH_DETAILS_XFORM )
            assert response.status_code == 200
