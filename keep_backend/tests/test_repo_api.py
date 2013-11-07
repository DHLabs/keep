'''
    Makes HTTP requests to each of our Repo API functions to ensure that
    basic API authentication, authorization, and functionality is available.
'''
#from django.contrib.auth.models import User
from urllib2 import HTTPError
from tests import ApiTestCase


class RepoApiV1Tests( ApiTestCase ):

    AUTH_DETAILS = { 'format':  'json',
                     'user':    'admin',
                     'key':     '35f7d1fb1890bdc05f9988d01cf1dcab' }

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

        assert 'meta' in response and 'objects' in response
        assert len( response[ 'objects' ] ) > 0

        return response

    def test_repo_list_fail( self ):
        '''
            Test failure states for the repo listings API.
        '''
        error_thrown = False
        response = None
        try:
            data = {'format': 'json', 'user': 'doesntexist'}
            response = self.open( '/repos/', data )
        except HTTPError as e:
            error_thrown = True
            assert e.code == 401

        assert error_thrown
        assert response is None

    def test_repo_detail( self ):
        '''
            Test if we can list the repo details for a specific repo for a
            test user.
        '''

        response = self.test_repo_list()
        repo = response[ 'objects' ][0][ 'id' ]

        # Grab the repo details
        response = self.open( '/repos/%s' % ( repo ), self.AUTH_DETAILS )

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
        response = self.open( '/repos/%s' % ( repo[ 'id' ] ), self.AUTH_DETAILS_OTHER )

        assert response is not None
        assert 'id' in response and response[ 'id' ] == repo[ 'id' ]

    def test_repo_detail_fail_nonexistent_user( self ):
        '''
            Test failure state for the repo detail API when passed a
            non-existent user
        '''
        # Get the list of repos for the test user
        response = self.test_repo_list()
        repo = response[ 'objects' ][0][ 'id' ]

        error_thrown = False
        response = None

        try:
            # Grab the repo details under a non-existent user
            data = {'format': 'json', 'user': 'doesntexist'}
            response = self.open( '/repos/%s' % ( repo ), data )
        except HTTPError as e:
            error_thrown = True
            assert e.code == 401

        assert error_thrown
        assert response is None

    def test_repo_detail_fail_different_user( self ):
        '''
            Test failure state for the repo detail API when passed a
            user who does not own the current repo
        '''
        # Get the list of repos for the test user
        response = self.test_repo_list()
        for repo in response.get( 'objects' ):
            if repo.get( 'is_public' ) == False:
                break

        if repo.get( 'is_public' ):
            return

        error_thrown = False
        response = None
        try:
            # Grab the repo details under a non-existent user
            response = self.open( '/repos/%s' % ( repo.get( 'id' ) ), self.AUTH_DETAILS_OTHER )
        except HTTPError as e:
            error_thrown = True
            assert e.code == 404

        assert error_thrown
        assert response is None
