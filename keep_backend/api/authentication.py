from django.contrib.auth.models import User

from tastypie.authentication import Authentication

from twofactor.models import UserAPIToken


class ApiTokenAuthentication( Authentication ):
    def is_authenticated( self, request, **kwargs ):
        username = request.GET.get( 'user', None )
        key = request.GET.get( 'key', None )

        # Ensure the correct parameters were passed in
        if username is None or key is None:
            return False

        # Check to see if we have this user AND that they API key
        # matches those that belong to said user
        user = User.objects.get( username=username )
        tokens = UserAPIToken.objects.filter( user=user )
        if user is None or len( tokens ) == 0:
            return False

        for token in tokens:
            if token.key == key:
                return True

        # No matching key? Deny access.
        return False

    def get_identifier( self, request ):
        return request.GET.get( 'user' )
