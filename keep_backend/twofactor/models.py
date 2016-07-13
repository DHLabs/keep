import datetime
import googauth
import hmac
import uuid

from base64 import b32encode

from django.contrib.auth.models import User
from django.db import models

from socket import gethostname

from twofactor.util import encrypt_value, decrypt_value, get_google_url
from twofactor.util import random_seed


class UserAuthToken(models.Model):
    user = models.OneToOneField("auth.User")
    encrypted_seed = models.CharField(max_length=120)  # fits 16b salt+40b seed

    created_datetime = models.DateTimeField(
        verbose_name="created", auto_now_add=True)
    updated_datetime = models.DateTimeField(
        verbose_name="last updated", auto_now=True)

    def save( self, *args, **kwargs ):
        self.encrypted_seed = encrypt_value( random_seed() )
        return super( UserAuthToken, self ).save( *args, **kwargs )

    def check_auth_code(self, auth_code):
        """
        Checks whether `auth_code` is a valid authentication code for this
        user, at the current time.
        """

        secret_key = b32encode( decrypt_value( self.encrypted_seed ) )
        val = googauth.verify_time_based( secret_key,
                                          str( auth_code ), window=5 )
        return val is not None

    def google_url(self, name=None):
        """
        The Google Charts QR code version of the seed, plus an optional
        name for this (defaults to "username@hostname").
        """
        if not name:
            username = self.user.username
            hostname = gethostname()
            name = "%s@%s" % (username, hostname)

        return get_google_url(
            decrypt_value(self.encrypted_seed),
            name
        )

    def b32_secret(self):
        """
        The base32 version of the seed (for input into Google Authenticator
        and similar soft token devices.
        """
        return b32encode(decrypt_value(self.encrypted_seed))


class UserAPIToken( models.Model ):
    user        = models.ForeignKey( User )
    name        = models.CharField( max_length=256, blank=True, default='' )
    key         = models.CharField( max_length=256, blank=True, default='' )
    created     = models.DateTimeField( default=datetime.datetime.now )

    def __unicode__( self ):
        return u'%s for %s' % ( self.key, self.user )

    def save( self, *args, **kwargs ):
        if not self.key:
            self.key = self.generated_key()

        return super( UserAPIToken, self ).save( *args, **kwargs )

    def generated_key( self ):
        new_uuid = uuid.uuid4()
        return hmac.new( str( new_uuid ) ).hexdigest()
