'''
    Makes HTTP requests to each of our Repo API functions to ensure that
    basic API authentication, authorization, and functionality is available.
'''
import json

from django.test import Client

from tests import ApiTestCase


class RepoApiV1SessionTests( ApiTestCase ):

    AUTH_DETAILS = { 'format':  'json',
                     'user':    'admin' }

    def login( self ):
        self.client.post( '/accounts/login/', { 'username': 'admin',
                                                'password': 'test',
                                                'token': ''} )

    def logout( self ):
        self.client.get( '/accounts/logout/' )

    def test_repo_list( self ):

        self.login()

        # Get the list of repos for the test user
        response = self.open( '/repos/', self.AUTH_DETAILS )
        response = json.loads( response.content )

        self.logout()

        assert 'meta' in response and 'objects' in response
        assert len( response[ 'objects' ] ) > 0

        return response

    def test_repo_detail( self ):

        response = self.test_repo_list()

        self.login()

        for repo in response[ 'objects' ]:
            response = self.open( '/repos/%s/' % ( repo.get( 'id' ) ), self.AUTH_DETAILS )
            response = json.loads( response.content )
            assert response[ 'id' ] == repo.get( 'id' )

        self.logout()

    def test_repo_list_fail( self ):

        self.logout()

        # Not logged in and no user query.
        response = self.open( '/repos/', {} )
        assert response.status_code == 401


class RepoApiV1KeyTests( ApiTestCase ):

    AUTH_DETAILS = { 'format':  'json',
                     'user':    'admin',
                     'key':     '35f7d1fb1890bdc05f9988d01cf1dcab' }

    INVALID_AUTH = { 'format':  'json',
                     'user':    'admin',
                     'key':     'invalid_key' }

    AUTH_DETAILS_OTHER = {  'format':  'json',
                            'user':    'test_user',
                            'key':     '35f7d1fb1890bdc05f9988d01cf1dcab' }

    def test_repo_list( self ):
        '''
            Test if we can list the repos for the test user.

            Returns
            -------
            response : dict
                This is the full JSON response converted into a python
                dictionary.
        '''

        # Get the list of repos for the test user
        response = self.open( '/repos/', self.AUTH_DETAILS )
        response = json.loads( response.content )

        assert 'meta' in response and 'objects' in response
        assert len( response[ 'objects' ] ) > 0

        return response

    def test_repo_list_fail( self ):
        '''
            Test failure states for the repo listings API.
        '''
        data = {'format': 'json', 'user': 'doesntexist'}
        response = self.open( '/repos/', data )

        assert response.status_code == 401

    def test_repo_detail( self ):
        '''
            Test if we can list the repo details for a specific repo for a
            test user.
        '''

        response = self.test_repo_list()
        repo = response[ 'objects' ][0][ 'id' ]

        # Grab the repo details
        response = self.open( '/repos/%s/' % ( repo ), self.AUTH_DETAILS )
        response = json.loads( response.content )

        assert response is not None
        assert 'id' in response and response[ 'id' ] == repo

        return response

    def test_repo_detail_public( self ):
        '''
            Test accessing public repo details
        '''

        response = self.test_repo_list()

        # Find the first public repository
        for repo in response[ 'objects' ]:
            if repo.get( 'is_public', False ):
                break

        # Grab the repo details under a different user
        response = self.open( '/repos/%s/' % ( repo[ 'id' ] ), self.AUTH_DETAILS_OTHER )
        response = json.loads( response.content )

        assert response is not None
        assert 'id' in response and response[ 'id' ] == repo[ 'id' ]

    def test_repo_detail_fail_nonexistent_user( self ):
        '''
            Test failure state for the repo detail API when passed a
            non-existent user
        '''
        # Get the list of repos for the test user
        response = self.test_repo_list()

        for repo in response.get( 'objects' ):

            # Grab the repo details under a non-existent user
            data = {'format': 'json', 'user': 'doesntexist'}
            response = self.open( '/repos/%s/' % ( repo.get( 'id' ) ), data )

            assert response.status_code == 401

    def test_repo_detail_fail_different_user( self ):
        '''
            Test failure state for the repo detail API when passed a
            user who does not own the current repo
        '''
        # Get the list of repos for the test user
        response = self.test_repo_list()
        for repo in response.get( 'objects' ):

            # Grab the repo details under a non-existent user
            response = self.open( '/repos/%s/' % ( repo.get( 'id' ) ), self.AUTH_DETAILS_OTHER )

            if repo.get( 'is_public' ):
                assert response.status_code == 200
            else:
                assert response.status_code == 404

    def test_invalid_api_key( self ):
        '''
            Attempt to access the repo API using an invalid API key.
        '''
        response = None

        # Attempt with a valid user but invalid API key
        response = self.open( '/repos/', self.INVALID_AUTH )

        assert response.status_code == 401
