from django.contrib.auth.models import User

from tastypie.authentication import Authentication

from twofactor.models import UserAPIToken


class ApiTokenAuthentication( Authentication ):
    def is_authenticated( self, request, **kwargs ):
        return True

        if request.user.is_authenticated():
            return True

        if request.method == 'POST':
            username = request.POST.get( 'user', None )
            key = request.POST.get( 'key', None )
        else:
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

        if request.method == 'POST':
            return request.POST.get( 'user' )
        else:
            return request.GET.get( 'user' )
