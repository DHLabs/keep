from backend.db import MongoDBResource, Document
from backend.xforms.serializer import XFormSerializer

from django.conf.urls import url
from django.contrib.auth.models import User

from tastypie import fields
from tastypie.utils import trailing_slash

from twofactor.api_auth import ApiTokenAuthentication


class FormResource( MongoDBResource ):
    id          = fields.CharField( attribute='_id' )
    name        = fields.CharField( attribute='name', null=True )
    title       = fields.CharField( attribute='title', null=True )
    default_language = fields.CharField( attribute='default_language',
                                         null=True )
    id_string   = fields.CharField( attribute='id_string', null=True )
    type        = fields.CharField( attribute='type', null=True )
    children    = fields.ListField( attribute='children', null=True )
    owner       = fields.CharField( attribute='user', null=True )

    class Meta:
        collection = 'survey'
        resource_name = 'forms'
        object_class = Document

        list_allowed_methods = [ 'get' ]
        detail_allowed_methods = [ 'get' ]

        # Only return JSON & XForm xml
        serializer = XFormSerializer()

        # Ensure we have an API token before returning any data.
        authentication = ApiTokenAuthentication()

        # TODO: Authorize based on sharing preferences.
        # authorization = BlahBlah()

        # Don't include resource uri
        include_resource_uri = False

    def dehydrate_owner(self, bundle):
        '''
        Convert user ids into a more informative username when displaying
        results
        '''
        user = User.objects.get( id=bundle.data['owner'] )
        return user.username

    def override_urls( self ):
        return [
            url( r"^(?P<resource_name>%s)/(?P<username>\w+)/formList%s$" %
                ( self._meta.resource_name, trailing_slash() ),
                self.wrap_view('formList'),
                name="api_form_list"),
        ]

    def formList( self, request, **kwargs ):
        return self.create_response( request, [] )
