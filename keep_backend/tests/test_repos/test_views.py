from tests import ViewTestCase

from repos.models import Repository


class RepoViewTests( ViewTestCase ):

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
