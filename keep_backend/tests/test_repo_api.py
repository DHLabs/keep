'''
    Makes HTTP requests to each of our Repo API functions to ensure there are
    no templating/etc errors on the pages.
'''
#from django.contrib.auth.models import User
from urllib2 import HTTPError
from tests import ApiTestCase


class RepoApiV1Tests( ApiTestCase ):

    def test_repo_list( self ):
        '''
            Test if we can list the repos for the test user
        '''
        response = self.open( '/repos/', {'format': 'json', 'user': 'admin'} )

        assert 'meta' in response and 'objects' in response
        assert len( response[ 'objects' ] ) > 0

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

        # Get the list of repos for the test user
        response = self.open( '/repos/', {'format': 'json', 'user': 'admin'} )
        repo = response[ 'objects' ][0][ 'id' ]

        # Grab the repo details
        response = self.open( '/repos/%s' % ( repo ),
                              {'format': 'json', 'user': 'admin'} )

        assert response is not None
        assert 'id' in response and response[ 'id' ] == repo

    def test_repo_detail_public( self ):
        '''
            Test accessing public repo details
        '''
        # Get the list of repos for the test user
        response = self.open( '/repos/', {'format': 'json', 'user': 'admin'} )

        for repo in response[ 'objects' ]:
            if 'public' in repo and repo[ 'public' ]:
                break

        # Grab the repo details under a different user
        data = {'format': 'json', 'user': 'test_user'}
        response = self.open( '/repos/%s' % ( repo[ 'id' ] ), data )

        assert response is not None
        assert 'id' in response and response[ 'id' ] == repo[ 'id' ]

    def test_repo_detail_fail_nonexistent_user( self ):
        '''
            Test failure state for the repo detail API when passed a
            non-existent user
        '''
        # Get the list of repos for the test user
        response = self.open( '/repos/', {'format': 'json', 'user': 'admin'} )
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
        response = self.open( '/repos/', {'format': 'json', 'user': 'admin'} )
        repo = response[ 'objects' ][0][ 'id' ]

        error_thrown = False
        response = None

        try:
            # Grab the repo details under a non-existent user
            data = {'format': 'json', 'user': 'test_user'}
            response = self.open( '/repos/%s' % ( repo ), data )
        except HTTPError as e:
            error_thrown = True
            assert e.code == 401

        assert error_thrown
        assert response is None
