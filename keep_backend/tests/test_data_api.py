'''
    Makes HTTP requests to each of our Data API functions to ensure there are
    no templating/etc errors on the pages.
'''
import json

from tests import ApiTestCase


class DataApiV1KeyTests( ApiTestCase ):

    AUTH_DETAILS = { 'format':  'json',
                     'user':    'admin',
                     'key':     '35f7d1fb1890bdc05f9988d01cf1dcab' }

    INVALID_AUTH = { 'format':  'json',
                     'user':    'admin',
                     'key':     'invalid_key' }

    AUTH_DETAILS_OTHER = {  'format':  'json',
                            'user':    'test_user',
                            'key':     '35f7d1fb1890bdc05f9988d01cf1dcab' }


    def test_data_detail( self ):
        '''
            Test if we can list the repo details for a specific repo for a
            test user.
        '''
        # Get the list of repos for the test user
        repos = self.open( '/repos/', self.AUTH_DETAILS )
        repos = json.loads( repos.content )

        CSV_AUTH = dict( self.AUTH_DETAILS )
        CSV_AUTH[ 'format' ] = 'csv'

        for repo in repos.get( 'objects' ):
            response = self.open( '/data/%s/' % ( repo.get( 'id' ) ), self.AUTH_DETAILS )
            assert response.status_code == 200

            response = self.open( '/data/%s/' % ( repo.get( 'id' ) ), CSV_AUTH )
            print response.status_code == 200

    def test_data_detail_failures( self ):
        '''
            Test failure state when querying for repo data under a
            non-permitted user
        '''
        # Get the list of repos for the test user
        repos = self.open( '/repos/', self.AUTH_DETAILS )
        repos = json.loads( repos.content )

        for repo in repos.get( 'objects' ):

            # Test valid user/key
            response = self.open( '/data/%s/' % ( repo.get( 'id' ) ), self.AUTH_DETAILS_OTHER )
            if repo.get( 'is_public' ):
                assert response.status_code == 200
            else:
                assert response.status_code == 401

            # Test invalid user/key
            response = self.open( '/data/%s/' % ( repo.get( 'id' ) ), self.INVALID_AUTH )
            assert response.status_code == 401

    def test_data_post( self ):
        '''
            Test if we can successfully post data to the API for a repo.
        '''
        # Get the list of repos for the test user
        repos = self.open( '/repos/', self.AUTH_DETAILS )
        repos = json.loads( repos.content )

        for repo in repos.get( 'objects' ):

            # Grab the list of datapoints for this repo
            response = self.open( '/data/%s/' % ( repo.get( 'id' ) ), self.AUTH_DETAILS )
            response = json.loads( response.content )

            beforeCount = response.get( 'meta' ).get( 'count' )

            new_data = { 'name': 'Bob Dole', 'age': 20, 'gender': 'male' }

            # Attempt to post data to the repo.
            response = self.open( '/repos/%s/?user=%s&key=%s&format=%s' % ( repo.get( 'id' ),
                                                                            self.AUTH_DETAILS[ 'user' ],
                                                                            self.AUTH_DETAILS[ 'key' ],
                                                                            self.AUTH_DETAILS[ 'format' ] ),
                                  new_data,
                                  method='POST' )
            response = json.loads( response.content )

            assert response.get( 'success' )

            response = self.open( '/data/%s/' % ( repo.get( 'id' ) ), self.AUTH_DETAILS )
            response = json.loads( response.content )

            assert response.get( 'meta' ).get( 'count' ) == ( beforeCount + 1 )
