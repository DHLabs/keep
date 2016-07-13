import json

from django.core.urlresolvers import reverse
from tests import ViewTestCase

from organizations.models import Organization


class OrgViewTests( ViewTestCase ):

    def test_add_member_accept( self ):

        org = self.test_new()
        self.login()

        # Request a member to join
        url = reverse( 'organization_member_add', kwargs={'org': org.name, 'user': 'test_user'} )
        response = self.client.post( url )
        self.assertEqual( response.status_code, 200 )

        # Attempt to accept member invitation under another account
        url = reverse( 'organization_member_accept', kwargs={'org': org.name, 'user': 'test_user'})
        response = self.client.get( url )
        self.assertEqual( response.status_code, 404 )

        self.logout()

        # Login with our test user and accept the member invitation
        self.login( username='test_user', password='test' )
        response = self.client.get( url )
        self.assertEqual( response.status_code, 302 )
        self.logout()

        org.delete()

    def test_add_member_ignore( self ):

        org = self.test_new()
        self.login()

        # Request a member to join
        url = reverse( 'organization_member_add', kwargs={'org': org.name, 'user': 'test_user'} )
        response = self.client.post( url )
        self.assertEqual( response.status_code, 200 )

        # Attempt to accept member invitation under another account
        url = reverse( 'organization_member_ignore', kwargs={'org': org.name, 'user': 'test_user'})
        response = self.client.get( url )
        self.assertEqual( response.status_code, 404 )

        self.logout()

        # Login with our test user and accept the member invitation
        self.login( username='test_user', password='test' )
        response = self.client.get( url )
        self.assertEqual( response.status_code, 302 )
        self.logout()

        org.delete()

    def test_dashboard( self ):

        org = self.test_new()
        url = reverse( 'organization_dashboard', kwargs={ 'org': org.name } )

        self.login()

        response = self.client.get( url )
        self.assertEqual( response.status_code, 200 )

        self.logout()
        org.delete()

    def test_delete( self ):

        org = self.test_new()
        url = reverse( 'organization_delete', kwargs={ 'org': org.name } )

        self.login()

        response = self.client.get( url )
        self.assertEqual( response.status_code, 302 )

        self.logout()

    def test_new( self ):

        self.login()

        url = reverse( 'organization_new' )

        # Test GET response
        response = self.client.get( url )
        self.assertEqual( response.status_code, 200 )

        # Test POST response
        org_data = {
            'name': 'test_org',
            'gravatar': '' }
        response = self.client.post( url, org_data )
        self.assertEqual( response.status_code, 302 )

        self.logout()

        return Organization.objects.get( name='test_org' )

    def test_new_repo( self ):

        org = self.test_new()
        self.login()

        url = reverse( 'organization_repo_new', kwargs={'org': org.name} )

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
        org.delete()