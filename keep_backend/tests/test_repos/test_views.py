from tests import ViewTestCase

from repos.models import Repository


class RepoViewTests( ViewTestCase ):

    def test_webform( self ):
        '''
            URL Tested: /<username>/<repo_name>/webform/
        '''
        repos = Repository.objects.all()

        self.login()
        for repo in repos:
            response = self.client.get( '/%s/%s/webform/' % ( repo.user.username, repo.name ) )
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
            response = self.client.post( '/%s/%s/webform/' % ( repo.user.username, repo.name ),
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
