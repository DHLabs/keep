import json

from django.core.urlresolvers import reverse
from tests import ViewTestCase

from repos.models import Repository


class RepoViewTests( ViewTestCase ):

    def test_delete( self ):

        # Add a test repo and then delete it.
        self.test_new()
        repo = Repository.objects.get( name='new_test' )
        self.assertNotEqual( repo, None )

        # Attempt to delete repo
        self.login()

        url = reverse( 'repo_delete', kwargs={ 'repo_id': repo.mongo_id } )
        response = self.client.get( url )
        self.assertEqual( response.status_code, 302 )
        repos = Repository.objects.filter( name='new_test' )
        self.assertEqual( len( repos ), 0 )

        self.logout()

    def test_edit( self ):
        '''
            URL Tested: /repo/edit/<repo_id>/
        '''

        repos = Repository.objects.all()

        self.login()
        for repo in repos:

            url = reverse( 'repo_edit', kwargs={ 'repo_id': repo.mongo_id } )

            # Access the editing page
            response = self.client.get( url )
            self.assertEqual( response.status_code, 200 )

            # Attempt to "edit" the repo.
            edit_data = {
                'name': repo.name + '_edited',
                'desc': repo.description,
                'survey_json': json.dumps( {
                    'type': 'survey',
                    'children': repo.fields() } )
            }
            response = self.client.post( url, edit_data )
            self.assertEqual( response.status_code, 302 )

        self.logout()

    def test_new( self ):
        '''
            URL Tested: /repo/new/
        '''

        self.login()

        url = reverse( 'repo_new' )

        # Test GET response
        response = self.client.get( url )
        self.assertEqual( response.status_code, 200 )

        # Test POST response
        repo_data = {
            'name': 'new_test',
            'desc': 'description',
            'privacy': 'private',
            'survey_json': json.dumps( {
                'type': 'survey',
                'children': [ { 'type': 'text',
                                'name': 'name',
                                'label': 'What\'s your name?' }]
            })
        }
        response = self.client.post( url, repo_data )
        self.assertEqual( response.status_code, 302 )

        self.logout()

    def test_share( self ):
        '''
            URL Tested: /repo/share/<repo_id>/
        '''

        repos = Repository.objects.all()

        self.login()
        for repo in repos:

            url = reverse( 'share_repo', kwargs={ 'repo_id': repo.mongo_id } )

            # Test basic error handling
            response = self.client.get( url )
            self.assertEqual( response.status_code, 404 )

            # Test attempting to change your own permissions
            response = self.client.get( url, { 'username': repo.user.username } )
            self.assertEqual( response.status_code, 401 )

            # Test add permissions to a user
            response = self.client.post( url, { 'username': 'test_user', 'permissions': 'view_repository' } )
            self.assertEqual( response.status_code, 200 )

            # Test deleting permissions from a user
            response = self.client.delete( url, json.dumps( { 'username': 'test_user' } ) )
            self.assertEqual( response.status_code, 204 )

        self.logout()

    def test_webform( self ):
        '''
            URL Tested: /<username>/<repo_name>/webform/
        '''
        repos = Repository.objects.all()

        self.login()
        for repo in repos:
            kwargs = { 'username': repo.user.username, 'repo_name': repo.name }
            response = self.client.get( reverse( 'repo_webform', kwargs=kwargs ) )
            self.assertEqual( response.status_code, 200 )
        self.logout()

    def test_webform_post( self ):
        '''
            URL Tested: /<username>/<repo_name>/webform/

            Test posting data to a webform.
        '''

        repos = Repository.objects.all()

        # LOGGED IN
        self.login()
        for repo in repos:

            before_count = repo.data().count()

            test_data = { 'name': 'test_name' }

            kwargs = { 'username': repo.user.username, 'repo_name': repo.name }
            response = self.client.post( reverse( 'repo_webform', kwargs=kwargs ),
                                         test_data )

            after_count = repo.data().count()

            self.assertEqual( response.status_code, 302 )
            self.assertEqual( before_count + 1, after_count )

        self.logout()

        # NOT LOGGED IN
        for repo in repos:

            before_count = repo.data().count()

            test_data = { 'name': 'test_name' }
            response = self.client.post( '/%s/%s/webform/' % ( repo.user.username, repo.name ),
                                         test_data )

            after_count = repo.data().count()

            self.assertEqual( response.status_code, 200 )
            self.assertEqual( before_count + 1, after_count )

    def test_webform_failure( self ):
        repos = Repository.objects.all()

        self.login()

        response = self.client.get( '/invalid_user/invalid_repo/webform/' )
        self.assertEqual( response.status_code, 404 )

        response = self.client.get( '/admin/invalid_repo/webform/' )
        self.assertEqual( response.status_code, 404 )

        self.logout()

    def test_repo_viz( self ):
        '''
            URL Tested: /<username>/<repo_name>/

            Tests viewing the data for a specific data repository. We test both
            non-logged in and logged in sessions to the same set of repos.
        '''
        repos = Repository.objects.all()

        ## NOT LOGGED IN
        for repo in repos:
            response = self.client.get( '/%s/%s/' % ( repo.user.username, repo.name ) )

            # Test that the repo is correctly shown as unauthorized if it is not
            # public.
            if repo.is_public:
                self.assertEqual( response.status_code, 200 )
            else:
                self.assertEqual( response.status_code, 401 )

        ## LOGGED IN
        self.login()
        for repo in repos:
            response = self.client.get( '/%s/%s/' % ( repo.user.username, repo.name ) )

            self.assertEqual( response.status_code, 200 )
        self.logout()

    def test_repo_viz_failure( self ):
        '''
            URL Tested: /<username>/<repo_name>/

            Testing for correct handling of failures
        '''

        self.login()

        response = self.client.get( '/invalid_user/invalid_repo/' )
        self.assertEqual( response.status_code, 404 )

        response = self.client.get( '/admin/invalid_repo/' )
        self.assertEqual( response.status_code, 404 )

        self.logout()
