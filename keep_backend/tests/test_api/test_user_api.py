'''
    Makes HTTP requests to each of our User API functions to ensure there are
    no templating/etc errors on the pages.
'''
import json

from tests import ApiTestCase


class UserApiTests( ApiTestCase ):

    def test_autocomplete( self ):
        '''
        '''
        response = self.open( '/user/', { 'username__icontains': 'admin' } )
        assert response.status_code == 200

        response = json.loads( response.content )
        assert response.get( 'meta' ).get( 'total_count' ) == 1

    def test_errors( self ):
        response = self.open( '/user/', {} )
        assert response.status_code == 400
