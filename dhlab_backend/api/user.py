from django.contrib.auth.models import User

from tastypie.exceptions import BadRequest
from tastypie.resources import ModelResource


class UserResource( ModelResource ):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'

        list_allowed_methods = [ 'get' ]
        detail_allowed_methods = []

        excludes = [ 'email',
                     'password',
                     'is_superuser',
                     'is_staff',
                     'is_active',
                     'date_joined',
                     'first_name',
                     'last_name',
                     'last_login' ]

        filtering = {
            'username': ( 'icontains', )
        }

    def build_filters( self, filters=None ):
        '''
            Since we're only using this API to search for users, require that
            a filter be in the API call.
        '''
        if 'username__icontains' not in filters:
            raise BadRequest
        return super( UserResource, self ).build_filters( filters )
