import os
import shlex
import subprocess
import urllib
import urllib2

from django.test import Client, LiveServerTestCase, TestCase

from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver


class HttpTestCase( LiveServerTestCase ):

    @classmethod
    def setUpClass( cls ):
        cls.selenium = WebDriver()
        #cls.selenium = webdriver.PhantomJS()
        #cls.selenium.set_window_size( 1024, 768 )

        with open( os.devnull, 'w' ) as devnull:
            testdb = 'mongorestore -d test --drop ../_data/mongo-test/dhlab'
            subprocess.call( shlex.split( testdb ),
                             stdout=devnull,
                             stderr=devnull )

        super( HttpTestCase, cls ).setUpClass()

    @classmethod
    def tearDownClass( cls ):
        cls.selenium.quit()
        super( HttpTestCase, cls ).tearDownClass()

    def open( self, url ):
        self.selenium.get( '%s%s' % ( self.live_server_url, url ) )


class ApiTestCase( TestCase ):

    fixtures = [ '../_data/fixtures/test_data.yaml' ]

    @classmethod
    def setUpClass( cls ):

        cls.client = Client()

        with open( os.devnull, 'w' ) as devnull:
            testdb = 'mongorestore -d test --drop ../_data/mongo-test/dhlab'
            subprocess.call( shlex.split( testdb ),
                             stdout=devnull,
                             stderr=devnull )

        super( ApiTestCase, cls ).setUpClass()

    def openRaw( self, url, params ):
        final_url = '%s%s' % ( self.live_server_url, url )
        return urllib2.urlopen( final_url, params ).read()

    def open( self, url, params, method='GET', format='JSON' ):
        final_url = '/api/v1' + url

        if method == 'GET':
            return self.client.get( final_url, params )
        else:
            return self.client.post( final_url, params )

