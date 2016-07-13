import json

from django.core.urlresolvers import reverse
from tests import ViewTestCase
from twofactor.models import UserAPIToken


class BackendViewTests( ViewTestCase ):

    def test_api_keys( self ):

        self.login()

        url = reverse( 'generate_api_key' )
        response = self.client.get( url, {'name': 'test_key'} )
        self.assertEqual( response.status_code, 302 )

        token = UserAPIToken.objects.get( name='test_key' )
        url = reverse( 'delete_api_key', kwargs={ 'key': token.id } )
        response = self.client.get( url )
        self.assertEqual( response.status_code, 302 )

        self.logout()

    def test_dashboard( self ):

        self.login()

        url = reverse( 'user_dashboard', kwargs={'username': 'admin'} )
        response = self.client.get( url )
        self.assertEqual( response.status_code, 200 )

        url = reverse( 'user_dashboard', kwargs={'username': 'test_user'} )
        response = self.client.get( url )
        self.assertEqual( response.status_code, 200 )

        self.logout()

    def test_home( self ):

        url = reverse( 'home' )
        response = self.client.get( url )
        self.assertEqual( response.status_code, 200 )

        self.login()

        response = self.client.get( url )
        self.assertEqual( response.status_code, 302 )

        self.logout()

    def test_register( self ):

        url = reverse( 'registration_register' )
        response = self.client.get( url )
        self.assertEqual( response.status_code, 200 )

        reg_data = {
            'username': 'register_test',
            'email':    'foo@example.com',
            'password1': 'test',
            'password2': 'test' }
        response = self.client.post( url, reg_data )

    def test_resend_activation( self ):

        url = reverse( 'resend_activation' )
        response = self.client.get( url )
        self.assertEqual( response.status_code, 200 )

        response = self.client.post( url, { 'email': 'blah' } )
        self.assertEqual( response.status_code, 200 )


    def test_settings( self ):

        url = reverse( 'settings' )

        self.login()

        response = self.client.get( url )
        self.assertEqual( response.status_code, 200 )

        self.logout()
