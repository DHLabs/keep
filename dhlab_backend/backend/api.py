import json
import pymongo

from backend.db import db, MongoDBResource, Document
from backend.db import dehydrate_survey
from backend.serializers import CSVSerializer

from repos import validate_and_format
from openrosa.serializer import XFormSerializer

from bson import ObjectId

from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.http import HttpUnauthorized
from tastypie.utils.mime import build_content_type

# from twofactor.api_auth import ApiTokenAuthentication


class DataAuthorization( Authorization ):

    def read_list( self, object_list, bundle ):
        user = bundle.request.GET.get( 'user', None )

        try:
            user = User.objects.get( username=user )
        except ObjectDoesNotExist:
            raise ValueError

        return object_list.find( { 'user': user.id },
                                 { 'data': False, 'user': False } )\
                          .limit( 5 )\
                          .sort( 'timestamp', pymongo.DESCENDING )

    def read_detail( self, object_detail, bundle ):
        user = bundle.request.GET.get( 'user', None )

        try:
            user = User.objects.get( username=user )
        except ObjectDoesNotExist:
            return False

        if object_detail[ 'user' ] != user.id:
            return False

        return True


class RepoAuthorization( Authorization ):

    def read_list( self, object_list, bundle ):
        user = bundle.request.GET.get( 'user', None )

        try:
            user = User.objects.get( username=user )
        except ObjectDoesNotExist:
            raise ValueError

        return object_list.find({ 'user': user.id } )

    def read_detail( self, object_detail, bundle ):

        if object_detail.get( 'public', False ):
            return True

        user = bundle.request.GET.get( 'user', None )

        try:
            user = User.objects.get( username=user )
        except ObjectDoesNotExist:
            return False

        if object_detail[ 'user' ] != user.id:
            return False

        return True

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


class RepoResource( MongoDBResource ):
    id          = fields.CharField( attribute='_id' )
    name        = fields.CharField( attribute='name', null=True )
    title       = fields.CharField( attribute='title', null=True )
    default_language = fields.CharField( attribute='default_language',
                                         null=True )
    id_string   = fields.CharField( attribute='id_string', null=True )
    type        = fields.CharField( attribute='type', null=True )
    children    = fields.ListField( attribute='children', null=True )
    owner       = fields.IntegerField( attribute='user', null=True )
    public      = fields.BooleanField( attribute='public', default=False )

    class Meta:
        collection = 'survey'
        resource_name = 'repos'
        object_class = Document

        list_allowed_methods = [ 'get' ]
        detail_allowed_methods = [ 'get', 'post' ]

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

    def post_detail( self, request, **kwargs ):

        basic_bundle = self.build_bundle( request=request )

        # The find the suervey object associated with this form name & user
        repo = db.survey.find_one( { '_id': ObjectId( kwargs.get( 'pk' ) ) } )
        repo_user = repo[ 'user' ]

        # Are we authorized to post data here?
        if not self.authorized_create_detail( repo, basic_bundle ):
            return HttpUnauthorized()

        # Do basic validation of the data
        valid_data = validate_and_format( repo, request.POST )

        # Include some metadata with the survey data
        repo_data = {
            'user':         repo_user,
            # Survey/form ID associated with this data
            'repo':         repo[ '_id' ],

            # Survey name (used for feed purposes)
            'survey_label': repo[ 'name' ],

            # Timestamp of when this submission was received
            'timestamp':    datetime.utcnow(),
            # The validated & formatted survey data.
            'data':         valid_data
        }

        new_id = db.data.insert( repo_data )
        response_data = { 'success': True, 'id': str( new_id ) }
        return self.create_response( request, response_data )

    def dehydrate_owner(self, bundle):
        '''
        Convert user ids into a more informative username when displaying
        results
        '''
        user = User.objects.get( id=bundle.data['owner'] )
        return user.username
