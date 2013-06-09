import json
import os
import shlex
import subprocess
import urllib
import urllib2

from django.test import LiveServerTestCase

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


class ApiTestCase( LiveServerTestCase ):

    @classmethod
    def setUpClass( cls ):
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
        final_url = '%s%s' % ( self.live_server_url, '/api/v1' )
        final_url += url

        encoded_params = ''
        if params is not None:
            encoded_params = urllib.urlencode( params, True )

        if method == 'GET':
            final_url += '?' + encoded_params
            response = urllib2.urlopen( final_url )
        else:
            response = urllib2.urlopen( final_url, encoded_params )

        if format == 'JSON':
            return json.load( response )
        else:
            return response.read()
