import pymongo

from backend.db import db, MongoDBResource, Document
from backend.db import dehydrate_survey
from backend.serializers import CSVSerializer

from repos import validate_and_format
from openrosa.serializer import XFormSerializer

from bson import ObjectId

from django.conf.urls import url
from django.contrib.auth.models import User
from django.http import HttpResponse

from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest
from tastypie.http import HttpUnauthorized
from tastypie.resources import ModelResource
from tastypie.utils.mime import build_content_type

from backend.db import user_or_organization
from organizations.models import Organization
from repos.models import Repository

# from twofactor.api_auth import ApiTokenAuthentication


class DataAuthorization( Authorization ):

    def read_list( self, object_list, bundle ):

        user = bundle.request.GET.get( 'user', None )

        account = user_or_organization( user )
        if account is None:
            raise ValueError

        query = {}
        if isinstance( account, User ):
            query[ 'user' ] = account.id
        else:
            query[ 'org' ] = account.d

        return object_list.find( query,
                                 {'data': False, 'user': False, 'org': False})\
                          .limit( 5 )\
                          .sort( 'timestamp', pymongo.DESCENDING )

    def read_detail( self, object_detail, bundle ):
        user = bundle.request.GET.get( 'user', None )

        account = user_or_organization( user )

        if 'user' in object_detail:

            if isinstance( account, User ):
                if object_detail[ 'user' ] == account.id:
                    return True

        elif 'org' in object_detail:

            if isinstance( account, User ):
                org = Organization.objects.get( id=object_detail['org'] )
                if org.has_user( account ):
                    return True

            elif isinstance( account, Organization ):
                if object_detail[ 'org' ] == account.id:
                    return True

        return False


class RepoAuthorization( Authorization ):

    def read_list( self, object_list, bundle ):
        user = bundle.request.GET.get( 'user', None )

        account = user_or_organization( user )
        if account is None:
            raise ValueError

        if isinstance( account, User ):
            return object_list.find({ 'user': account.id } )
        else:
            return object_list.find({ 'org': account.id } )

    def read_detail( self, object_detail, bundle ):

        account = bundle.request.GET.get( 'user', None )
        account = user_or_organization( account )
        if account is None:
            return False

        return account.has_perm( 'view_repository', bundle.obj )

    def create_detail( self, object_detail, bundle ):
        return True


class DataResource( MongoDBResource ):
    id          = fields.CharField( attribute='_id' )
    repo_id     = fields.CharField( attribute='repo' )
    survey_label = fields.CharField( attribute='survey_label', null=True )
    timestamp   = fields.DateTimeField( attribute='timestamp' )
    data        = fields.DictField( attribute='data', null=True )

    class Meta:
        collection = 'data'
        resource_name = 'data'
        object_class = Document
        serializer = CSVSerializer()

        list_allowed_methos     = []
        detail_allowed_methods  = [ 'get', 'list' ]

        authorization = DataAuthorization()

    def get_detail( self, request, **kwargs ):

        # Grab the survey that we're querying survey data for
        repo_id = kwargs[ 'pk' ]

        try:
            basic_bundle = self.build_bundle( request=request )
            repo = db.survey.find_one( { '_id': ObjectId( repo_id ) } )

            if not self.authorized_read_detail( repo, basic_bundle ):
                return HttpUnauthorized()

            # Query the database for the data
            cursor = db.data.find( { 'repo': ObjectId( repo_id ) } )

            data = dehydrate_survey( cursor )

            return self.create_response( request, data )
        except ValueError:
            return HttpUnauthorized()


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
        # authentication = ApiTokenAuthentication()

        # TODO: Authorize based on sharing preferences.
        authorization = RepoAuthorization()

        # Don't include resource uri
        include_resource_uri = False

    def prepend_urls(self):
        return [

            url( regex=r"^(?P<resource_name>%s)/(?P<mongo_id>\w+)/$" % ( self._meta.resource_name ),
                 view=self.wrap_view('dispatch_detail'),
                 name="api_dispatch_detail"),

            url( regex=r"^(?P<resource_name>%s)/(?P<mongo_id>\w+)/manifest/$" % ( self._meta.resource_name ),
                 view=self.wrap_view('get_manifest'),
                 name="api_get_resource"),
        ]

    def create_response( self, request, data, response_class=HttpResponse,
                         **response_kwargs):
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

        media = list( set( self._grab_media( obj[ 'children' ] ) ) )
        media = [ ( med, base % ( obj['_id'], med ) ) for med in media ]

        response = { 'repo': obj[ '_id' ], 'manifest': media }
        return self.create_response( request, response )

    def post_detail( self, request, **kwargs ):

        basic_bundle = self.build_bundle( request=request )

        # The find the suervey object associated with this form name & user
        repo = db.survey.find_one( { '_id': ObjectId( kwargs.get( 'pk' ) ) } )

        account = None
        if 'user' in repo:
            account = repo[ 'user' ]
        elif 'org' in repo:
            account = repo[ 'org' ]

        account = user_or_organization( account )

        # Are we authorized to post data here?
        if not self.authorized_create_detail( repo, basic_bundle ):
            return HttpUnauthorized()

        # Do basic validation of the data
        valid_data = validate_and_format( repo, request.POST )

        new_id = Repository.add_data( repo=repo,
                                      data=valid_data,
                                      account=account )

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
        return bundle

    def dehydrate_id( self, bundle ):
        return bundle.obj.mongo_id

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
