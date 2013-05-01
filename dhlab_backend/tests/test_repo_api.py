'''
    Makes HTTP requests to each of our Repo API functions to ensure there are
    no templating/etc errors on the pages.
'''
#from django.contrib.auth.models import User
from tests import ApiTestCase


class RepoApiV1Tests( ApiTestCase ):

    def test_repo_list( self ):
        '''
            Test if we can list the repos for the test user
        '''
        response = self.open( '/repos/', {'format': 'json', 'user': 'admin'} )

        assert 'meta' in response and 'objects' in response
        assert len( response[ 'objects' ] ) > 0

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
        assert 'id' in response
        assert response[ 'id' ] == repo
