from backend.db import db
from backend.db import user_or_organization

from bson import ObjectId

from django.conf.urls import url
from django.http import HttpResponse

from tastypie.authentication import MultiAuthentication, SessionAuthentication, Authentication
from tastypie.exceptions import BadRequest
from tastypie.http import HttpUnauthorized, HttpNotFound
from tastypie.resources import ModelResource
from tastypie.utils.mime import build_content_type

from repos.models import Repository
from openrosa.serializer import XFormSerializer

from .authentication import ApiTokenAuthentication
from .authorization import RepoAuthorization


class RepoResource( ModelResource ):

    class Meta:
        queryset = Repository.objects.all()
        resource_name = 'repos'

        list_allowed_methods = [ 'get' ]
        detail_allowed_methods = [ 'get', 'post' ]

        excludes = [ 'mongo_id' ]

        # Only return JSON & XForm xml
        serializer = XFormSerializer()

        # Ensure we have an API token before returning any data.
        # TODO: Make sure this API token concept works with public/private
        # data.
        #authentication = MultiAuthentication( SessionAuthentication(), ApiTokenAuthentication() )
        authenication = Authentication()

        # TODO: Authorize based on sharing preferences.
        authorization = RepoAuthorization()

        # Don't include resource uri
        include_resource_uri = False

        filtering = {
            'study': ( 'exact', )
        }

    def prepend_urls(self):

        base_url = '^(?P<resource_name>%s)/' % ( self._meta.resource_name )

        return [

            url( regex=r"%s(?P<mongo_id>\w+)/$" % ( base_url ),
                 view=self.wrap_view('dispatch_detail'),
                 name="api_dispatch_detail"),

            url( regex=r"%s(?P<mongo_id>\w+)/manifest/$" % ( base_url ),
                 view=self.wrap_view('get_manifest'),
                 name="api_get_resource"),
        ]

    def build_filters( self, filters=None ):
        orm_filters = super( RepoResource, self ).build_filters( filters )

        if filters is None:
            return orm_filters

        if 'study' in filters:
            orm_filters[ 'study' ] = None

        return orm_filters

    def create_response( self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        Extracts the common "which-format/serialize/return-response" cycle.

        Mostly a useful shortcut/hook.
        """
        desired_format = self.determine_format(request)

        serialized = self.serialize(request, data, desired_format)
        response = response_class( content=serialized,
                                   content_type=build_content_type(desired_format),
                                   **response_kwargs )
        # FOR ODKCollect
        # If the device requests an xform add an OpenRosa header
        if desired_format == 'text/xml':
            response[ 'X-OpenRosa-Version'] = '1.0'
        return response

    def _grab_media( self, root ):

        media = []
        for field in root:
            if 'children' in field:
                media.extend( self._grab_media( field[ 'children' ] ) )
                continue

            if 'choices' in field:
                for choice in field[ 'choices' ]:
                    if 'media' in choice:
                        media.extend( choice[ 'media' ].values() )

            if 'media' in field:
                media.extend( field[ 'media' ].values() )

        return media

    def get_manifest( self, request, **kwargs ):
        base = 'http://s3.amazonaws.com/keep-media/%s/%s'

        bundle = self.build_bundle( request=request )
        obj = self.obj_get( bundle, **self.remove_api_resource_names(kwargs) )

        media = list( set( self._grab_media( obj.fields() ) ) )
        media = [ ( med, base % ( obj.mongo_id, med ) ) for med in media ]

        response = { 'repo': obj.mongo_id, 'manifest': media }
        return self.create_response( request, response )

    def post_detail( self, request, **kwargs ):

        #basic_bundle = self.build_bundle( request=request )

        user_accessing = request.GET.get( 'user', None )
        user = user_or_organization( user_accessing )
        if user is None:
            return HttpUnauthorized()

        repo = Repository.objects.get( mongo_id=kwargs.get( 'mongo_id' ) )
        if repo is None:
            return HttpNotFound()

        if not user.has_perm( 'add_data', repo ):
            return HttpUnauthorized()

        new_id = repo.add_data( request.POST, request.FILES )

        response_data = { 'success': True, 'id': str( new_id ) }
        return self.create_response( request, response_data )

    def dehydrate( self, bundle ):
        '''
            Add additional information to the Repository bundle.

            - fields:
                Fields are grabbed from MongoDB and appended to the bundle
                dictionary.
        '''
        repo_fields = db.repo.find_one( ObjectId( bundle.obj.mongo_id ) )
        bundle.data['children'] = repo_fields[ 'fields' ]

        if 'type' in repo_fields:
            bundle.data['type'] = repo_fields[ 'type' ]
        else:
            bundle.data['type'] = "survey"

        bundle.data['user'] = bundle.obj.user
        bundle.data['study'] = bundle.obj.study

        return bundle

    def dehydrate_id( self, bundle ):
        return bundle.obj.mongo_id

    def dehydrate_study( self, bundle ):
        return bundle.obj.study.name if bundle.obj.study else None

    def dehydrate_user( self, bundle ):
        '''
            Convert user ids into a more informative username when displaying
            results
        '''
        return bundle.obj.user.username if bundle.obj.user else None

    def dehydrate_org( self, bundle ):
        '''
            Convert organization ids into the more informative org name.
        '''
        return bundle.obj.org.name if bundle.obj.org else None
