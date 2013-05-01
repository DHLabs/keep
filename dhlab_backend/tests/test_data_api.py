'''
    Makes HTTP requests to each of our Data API functions to ensure there are
    no templating/etc errors on the pages.
'''
from tests import ApiTestCase


class DataApiV1Tests( ApiTestCase ):

    def test_data_detail( self ):
        '''
            Test if we can list the repo details for a specific repo for a
            test user.
        '''
        # Get the list of repos for the test user
        response = self.open( '/repos/', {'format': 'json', 'user': 'admin'} )
        repo = response[ 'objects' ][0][ 'id' ]

        # Grab the repo details
        response = self.open( '/data/%s' % ( repo ),
                              {'format': 'json', 'user': 'admin'} )

        assert response is not None
        assert len( response ) > 0
