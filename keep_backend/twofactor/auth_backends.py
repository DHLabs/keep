from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.conf import settings

from twofactor.models import UserAuthToken


class TwoFactorAuthBackend(ModelBackend):
    def authenticate(self, username=None, password=None, token=None):

        # Validate username and password first
        user_or_none = super( TwoFactorAuthBackend, self )\
                        .authenticate( username, password )

        # Don't bother checking for two-factor tokens when running in a
        # DEBUG environment.
        if settings.DEBUG or settings.TESTING:
            return user_or_none

        if user_or_none and isinstance(user_or_none, User):
            # Got a valid login. Now check token.
            try:
                user_token = UserAuthToken.objects.get(user=user_or_none)
            except UserAuthToken.DoesNotExist:
                # User doesn't have two-factor authentication enabled, so
                # just return the User object.
                return user_or_none

            validate = user_token.check_auth_code(token)
            if (validate == True):
                # Auth code was valid.
                return user_or_none
            else:
                # Bad auth code
                return None
        return user_or_none
