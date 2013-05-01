'''
    Makes HTTP requests to each of our Data API functions to ensure there are
    no templating/etc errors on the pages.
'''
from urllib2 import HTTPError
from tests import ApiTestCase


class DataApiV1Tests( ApiTestCase ):

    def test_data_list( self ):
        '''
            Test if we can list the last 5 data entries for a user
        '''
        # Grab the list of datapoints for this repo.
        response = self.open( '/data/', {'format': 'json', 'user': 'admin'} )
        assert response is not None

    def test_data_list_nonexistent_user( self ):
        '''
            Test failure state when listing data for a nonexistent user
        '''
        # Grab the list of datapoints for this repo.
        error_thrown = False
        response = None

        try:
            response = self.open( '/data/',
                                  {'format': 'json', 'user': 'doestexist'} )
        except HTTPError as e:
            error_thrown = True
            assert e.code == 401

        assert error_thrown and response is None

    def test_data_detail( self ):
        '''
            Test if we can list the repo details for a specific repo for a
            test user.
        '''
        # Get the list of repos for the test user
        response = self.open( '/repos/', {'format': 'json', 'user': 'admin'} )
        repo = response[ 'objects' ][0][ 'id' ]

        # Grab the list of datapoints for this repo.
        response = self.open( '/data/%s/' % ( repo ),
                              {'format': 'json', 'user': 'admin'} )

        assert response is not None
        assert len( response ) > 0

    def test_data_detail_different_user( self ):
        '''
            Test failure state when querying for repo data under a
            non-permitted user
        '''
        # Get the list of repos for the test user
        response = self.open( '/repos/', {'format': 'json', 'user': 'admin'} )
        repo = response[ 'objects' ][0][ 'id' ]

        error_thrown = False
        response = None
        try:
            response = self.open( '/data/%s/' % ( repo ),
                                  {'format': 'json', 'user': 'test_user'} )
        except HTTPError as e:
            error_thrown = True
            assert e.code == 401

        assert error_thrown and response is None

    def test_data_detail_nonexistent_user( self ):
        '''
            Test failure state when querying for repo data under a
            non-existent user
        '''
        # Get the list of repos for the test user
        response = self.open( '/repos/', {'format': 'json', 'user': 'admin'} )
        repo = response[ 'objects' ][0][ 'id' ]

        error_thrown = False
        response = None
        try:
            response = self.open( '/data/%s/' % ( repo ),
                                  {'format': 'json', 'user': 'doesntexist'} )
        except HTTPError as e:
            error_thrown = True
            assert e.code == 401

        assert error_thrown and response is None

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
