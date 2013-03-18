import pymongo

from backend.db import db, MongoDBResource, Document, decrypt_survey
from backend.serializers import CSVSerializer
from backend.xforms.serializer import XFormSerializer

from bson import ObjectId

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from tastypie import fields
from tastypie.authorization import Authorization

# from twofactor.api_auth import ApiTokenAuthentication


class BasicAuthorization( Authorization ):

    def read_list( self, object_list, bundle ):
        user = bundle.request.GET.get( 'user', None )

        try:
            user = User.objects.get( username=user )
        except ObjectDoesNotExist:
            return []

        return object_list.find({ 'user': user.id } )

    def read_detail( self, object_detail, bundle ):
        user = bundle.request.GET.get( 'user', None )

        try:
            user = User.objects.get( username=user )
        except ObjectDoesNotExist:
            raise ValueError

        if object_detail[ 'user' ] != user.id:
            raise ValueError

        return object_detail


class DataResource( MongoDBResource ):
    id          = fields.CharField( attribute='_id' )
    survey_id   = fields.CharField( attribute='survey' )
    timestamp   = fields.DateTimeField( attribute='timestamp' )
    data        = fields.DictField( attribute='data' )

    class Meta:
        collection = 'survey_data'
        resource_name = 'data'
        object_class = Document
        serializer = CSVSerializer()

        list_allowed_methos     = []
        detail_allowed_methods  = [ 'get', 'list' ]

        authorization = BasicAuthorization()

    def get_detail( self, request, **kwargs ):
        # Grab the survey that we're querying survey data for
        survey_id = kwargs[ 'pk' ]

        # Query the database for the data
        cursor = db.survey_data.find( { 'survey': ObjectId( survey_id ) })

        # Decrypt survey values
        data = []
        for row in cursor:
            row[ 'data' ] = decrypt_survey( row[ 'data' ] )
            row[ 'timestamp' ] = row[ 'timestamp' ].strftime( '%Y-%m-%dT%X' )
            data.append( row )

        return self.create_response( request, data )

    def get_list( self, request, **kwargs ):
        user = request.GET.get( 'user', None )
        user = User.objects.get( username=user )

        # Don't show encrypted data information and user id.
        # Limit to the last 5 submissions
        # Sort by latest submission first
        cursor = db.survey_data.find( { 'user': user.id },
                                      { 'data': False, 'user': False } )\
                               .limit( 5 )\
                               .sort( 'timestamp', pymongo.DESCENDING )

        # Format timestamp correctly such that Javascript can correctly parse
        # the information
        data = []
        for row in cursor:
            row[ 'timestamp' ] = row[ 'timestamp' ].strftime( '%Y-%m-%dT%X' )
            data.append( row )

        return self.create_response( request, data )


class FormResource( MongoDBResource ):
    id          = fields.CharField( attribute='_id' )
    name        = fields.CharField( attribute='name', null=True )
    title       = fields.CharField( attribute='title', null=True )
    default_language = fields.CharField( attribute='default_language',
                                         null=True )
    id_string   = fields.CharField( attribute='id_string', null=True )
    type        = fields.CharField( attribute='type', null=True )
    children    = fields.ListField( attribute='children', null=True )
    owner       = fields.IntegerField( attribute='user', null=True )

    class Meta:
        collection = 'survey'
        resource_name = 'forms'
        object_class = Document

        list_allowed_methods = [ 'get' ]
        detail_allowed_methods = [ 'get' ]

        # Only return JSON & XForm xml
        serializer = XFormSerializer()

        # Ensure we have an API token before returning any data.
        # TODO: Make sure this API token concept works with public/private
        # data.
        # authentication = ApiTokenAuthentication()

        # TODO: Authorize based on sharing preferences.
        authorization = BasicAuthorization()

        # Don't include resource uri
        include_resource_uri = False

    def dehydrate_owner(self, bundle):
        '''
        Convert user ids into a more informative username when displaying
        results
        '''
        user = User.objects.get( id=bundle.data['owner'] )
        return user.username
