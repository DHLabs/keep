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

        # Grab the list of datapoints for this repo.
        response = self.open( '/data/%s' % ( repo ),
                              {'format': 'json', 'user': 'admin'} )

        assert response is not None
        assert len( response ) > 0

    def test_data_post( self ):
        '''
            Test if we can successfully post data to the API for a repo.
        '''
        # Get the list of repos for the test user
        response = self.open( '/repos/', {'format': 'json', 'user': 'admin'} )
        repo = response[ 'objects' ][0][ 'id' ]

        # Grab the list of datapoints for this repo
        response = self.open( '/data/%s' % ( repo ),
                              {'format': 'json', 'user': 'admin'} )

        assert response is not None
        assert len( response ) > 0

        beforeLength = len( response )
        data = { 'name': 'Bob Dole', 'age': 20, 'gender': 'male' }

        # Attempt to post data to the repo.
        response = self.open( '/repos/%s/?user=admin&format=json' % ( repo ),
                              data,
                              method='POST' )

        assert response[ 'success' ]

        # Assert that the number of datapoints increased by one.
        response = self.open( '/data/%s' % ( repo ),
                              {'format': 'json', 'user': 'admin'} )
        assert len( response ) == beforeLength + 1
