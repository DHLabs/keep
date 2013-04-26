'''
    Makes HTTP requests to each of our pages to ensure there are no
    templating/etc errors on the pages.
'''
import googauth

from base64 import b32encode

from django.contrib.auth.models import User
from django.core import mail

from twofactor.util import decrypt_value
from twofactor.models import UserAuthToken

from tests import HttpTestCase


class HttpTests( HttpTestCase ):

    def test_index( self ):
        self.open( '/' )
        assert 'Keep' in self.selenium.title

    def test_login( self ):
        self.open( '/' )
        assert 'Keep' in self.selenium.title

        # Generate secret token
        user = User.objects.get(username='admin')
        user_token = UserAuthToken.objects.get(user=user)
        secret_key = b32encode( decrypt_value( user_token.encrypted_seed ) )
        token = googauth.generate_code( secret_key )

        self.selenium.find_element_by_id( 'id_username' ).send_keys( 'admin' )
        self.selenium.find_element_by_id( 'id_password' ).send_keys( 'test' )
        self.selenium.find_element_by_id( 'id_token' ).send_keys( token )
        self.selenium.find_element_by_id( 'login_btn' ).click()

        assert 'admin' in self.selenium.title

    def test_registration( self ):
        self.open( '/accounts/register' )

        self.selenium.find_element_by_id( 'id_username' ).send_keys( 'test' )
        self.selenium.find_element_by_id( 'id_email' ).send_keys( 't@foo.com' )
        self.selenium.find_element_by_id( 'id_password1' ).send_keys( 'test' )
        self.selenium.find_element_by_id( 'id_password2' ).send_keys( 'test' )
        self.selenium.find_element_by_id( 'register_btn' ).click()

        assert 'Registration Complete' in self.selenium.title
        assert len( mail.outbox ) == 1
