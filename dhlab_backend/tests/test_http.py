'''
    Makes HTTP requests to each of our pages to ensure there are no
    templating/etc errors on the pages.
'''
import googauth
import os

import selenium.webdriver.support.ui as ui

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
        self.open( '/accounts/login' )
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

    def test_create_repo_xls_form( self ):
        '''
            Tests the creation of a new repo
        '''
        self.test_login()

        repo_name = 'xls_repo'

        # Click on new repo button
        self.selenium.find_element_by_id( 'new_repo_btn' ).click()

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( repo_name )

        xform = os.path.abspath( '_data/test_docs/tutorial.xls' )
        self.selenium.find_element_by_id( 'id_xform_file' ).send_keys( xform )

        self.selenium.find_element_by_id( 'submit_btn' ).click()

        # Check that the new repo was created
        repo_table = '/html/body/div[2]/div/div[2]/table/tbody/tr/td[2]/a'
        repos = self.selenium.find_elements_by_xpath( repo_table )
        assert any( [ x.text == repo_name for x in repos ] )

    def test_create_repo_xml_form( self ):
        '''
            Tests the creation of a new repo
        '''
        self.test_login()

        repo_name = 'xml_repo'

        # Click on new repo button
        self.selenium.find_element_by_id( 'new_repo_btn' ).click()

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( repo_name )

        xform = os.path.abspath( '_data/test_docs/tutorial.xml' )
        self.selenium.find_element_by_id( 'id_xform_file' ).send_keys( xform )

        self.selenium.find_element_by_id( 'submit_btn' ).click()

        # Check that the new repo was created
        repo_table = '/html/body/div[2]/div/div[2]/table[1]/tbody/tr/td[2]/a'
        repos = self.selenium.find_elements_by_xpath( repo_table )
        assert any( [ x.text == repo_name for x in repos ] )

    def test_create_repo_xml_form_itext( self ):
        '''
            Tests the creation of a new repo
        '''
        self.test_login()

        repo_name = 'xml_repo_itext'

        # Click on new repo button
        self.selenium.find_element_by_id( 'new_repo_btn' ).click()

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( repo_name )

        xform = os.path.abspath( '_data/test_docs/zambia/Delivery.xml' )
        self.selenium.find_element_by_id( 'id_xform_file' ).send_keys( xform )

        self.selenium.find_element_by_id( 'submit_btn' ).click()

        # Check that the new repo was created
        repo_table = '/html/body/div[2]/div/div[2]/table/tbody/tr/td[2]/a'
        repos = self.selenium.find_elements_by_xpath( repo_table )
        assert any( [ x.text == repo_name for x in repos ] )

    def test_create_repo_existing( self ):
        '''
            Tests creation of a new repo with an existing name.
        '''
        self.test_login()

        # Click on new repo button
        self.selenium.find_element_by_id( 'new_repo_btn' ).click()

        # Fill out form
        self.selenium.find_element_by_id( 'id_name' ).send_keys( 'tutorial' )

        xform = os.path.abspath( '_data/test_docs/tutorial.xls' )
        self.selenium.find_element_by_id( 'id_xform_file' ).send_keys( xform )

        self.selenium.find_element_by_id( 'submit_btn' ).click()

        # Check that we correctly report an error
        error = '/html/body/div[2]/div/div/div/form/ul/li'
        elem = self.selenium.find_element_by_xpath( error )
        assert elem.text == 'Repository already exists with this name'

    def test_repo_detail( self ):
        '''
            Test access to a repo detail page.
        '''
        self.test_login()

        # Find the first data repo
        repo = '/html/body/div[2]/div/div[2]/table[1]/tbody/tr[1]/td[2]/a'
        repo = self.selenium.find_element_by_xpath( repo )

        repo_name = repo.text
        repo.click()

        assert repo_name in self.selenium.title

    def test_repo_share( self ):
        '''
            Test toggling repo sharing
        '''
        self.test_repo_detail()

        share = '//*[@id="viz_options"]/li[5]/a'
        share = self.selenium.find_element_by_xpath( share )
        share.click()

        wait = ui.WebDriverWait( self.selenium, 10 )
        wait.until( lambda driver: driver.find_element_by_id( 'sharing_toggle' ).is_displayed() )

        privacy = self.selenium.find_element_by_xpath( '//*[@id="privacy"]/div' )
        previous_privacy = privacy.text.strip()

        share = self.selenium.find_element_by_id( 'sharing_toggle' )
        share.click()

        if previous_privacy == 'PUBLIC':
            assert 'PRIVATE' in privacy.text
        else:
            assert 'PUBLIC' in privacy.text
