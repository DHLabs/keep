'''
    Makes HTTP requests to each of our pages to ensure there are no
    templating/etc errors on the pages.
'''
import googauth
import os

from base64 import b32encode

from django.contrib.auth.models import User
from django.core import mail

from twofactor.util import decrypt_value
from twofactor.models import UserAuthToken

from tests import HttpTestCase


class OrganizationHttpTests( HttpTestCase ):

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

    def test_create_organization( self ):
        self.test_login()

        org_name = 'test_org'

        new_org = '/html/body/div[2]/div/div[1]/div[1]/div[1]/a'
        self.selenium.find_element_by_xpath( new_org ).click()

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( org_name )

        submit = '/html/body/div[2]/div/div/div/form/div/button'
        self.selenium.find_element_by_xpath( submit ).click()

        # Check that the new repo was created
        org_list = '/html/body/div[2]/div/div[1]/div[1]/div/div/a'
        orgs = self.selenium.find_elements_by_xpath( org_list )
        assert any( [ x.text == org_name for x in orgs ] )

    def test_create_organization_with_gravatar( self ):
        self.test_login()

        org_name = 'test_org_2'

        new_org = '/html/body/div[2]/div/div[1]/div[1]/div[1]/a'
        self.selenium.find_element_by_xpath( new_org ).click()
        self.selenium.find_element_by_id( 'id_gravatar' )\
                     .send_keys( 'webmaster@distributedhealth.org' )

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( org_name )

        submit = '/html/body/div[2]/div/div/div/form/div/button'
        self.selenium.find_element_by_xpath( submit ).click()

        # Check that the new repo was created
        org_list = '/html/body/div[2]/div/div[1]/div[1]/div/div/a'
        orgs = self.selenium.find_elements_by_xpath( org_list )
        assert any( [ x.text == org_name for x in orgs ] )

    def test_create_organization_fail_invalid_name( self ):
        self.test_login()

        org_name = '1Q##$U ala2'

        new_org = '/html/body/div[2]/div/div[1]/div[1]/div[1]/a'
        self.selenium.find_element_by_xpath( new_org ).click()

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( org_name )

        submit = '/html/body/div[2]/div/div/div/form/div/button'
        self.selenium.find_element_by_xpath( submit ).click()

        # Check that we correctly report an error
        error = '/html/body/div[2]/div/div/div/form/ul/li'
        elem = self.selenium.find_element_by_xpath( error )
        assert elem.text == 'Organization name cannot have spaces or special characters'

    def test_create_organization_fail_reserved_name( self ):
        self.test_login()

        org_name = 'new'

        new_org = '/html/body/div[2]/div/div[1]/div[1]/div[1]/a'
        self.selenium.find_element_by_xpath( new_org ).click()

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( org_name )

        submit = '/html/body/div[2]/div/div/div/form/div/button'
        self.selenium.find_element_by_xpath( submit ).click()

        # Check that we correctly report an error
        error = '/html/body/div[2]/div/div/div/form/ul/li'
        elem = self.selenium.find_element_by_xpath( error )
        assert elem.text == 'Organization already exists with this name!'

    def test_create_organization_fail_existing( self ):
        self.test_login()

        org_name = 'test_user'

        new_org = '/html/body/div[2]/div/div[1]/div[1]/div[1]/a'
        self.selenium.find_element_by_xpath( new_org ).click()

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( org_name )

        submit = '/html/body/div[2]/div/div/div/form/div/button'
        self.selenium.find_element_by_xpath( submit ).click()

        # Check that we correctly report an error
        error = '/html/body/div[2]/div/div/div/form/ul/li'
        elem = self.selenium.find_element_by_xpath( error )
        assert elem.text == 'Organization already exists with this name!'
