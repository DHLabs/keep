'''
    Makes HTTP requests to each of our API functions to ensure there are no
    templating/etc errors on the pages.
'''
#from django.contrib.auth.models import User
from tests import ApiTestCase


class ApiV1Tests( ApiTestCase ):

    def test_repo_list( self ):
        response = self.open( '/repos/', {'format': 'json', 'user': 'admin'} )
        assert len( response[ 'objects' ] ) > 0
