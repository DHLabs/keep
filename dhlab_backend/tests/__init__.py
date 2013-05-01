import json
import os
import shlex
import subprocess
import urllib
import urllib2

from django.test import LiveServerTestCase

from selenium.webdriver.firefox.webdriver import WebDriver


class HttpTestCase( LiveServerTestCase ):

    @classmethod
    def setUpClass( cls ):
        cls.selenium = WebDriver()

        with open( os.devnull, 'w' ) as devnull:
            testdb = 'mongorestore -d test --drop ../_data/dhlab-backup/dhlab'
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
            testdb = 'mongorestore -d test --drop ../_data/dhlab-backup/dhlab'
            subprocess.call( shlex.split( testdb ),
                             stdout=devnull,
                             stderr=devnull )

        super( ApiTestCase, cls ).setUpClass()

    def open( self, url, params, method='GET' ):
        final_url = '%s%s' % ( self.live_server_url, '/api/v1' )
        final_url += url

        encoded_params = urllib.urlencode( params, True )

        if method == 'GET':
            final_url += '?' + encoded_params
            return json.load( urllib2.urlopen( final_url ) )

        return json.load( urllib2.urlopen( final_url, encoded_params ) )
