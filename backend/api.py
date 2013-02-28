from backend.db import db, MongoDBResource, Document, decrypt_survey
from backend.xforms.serializer import XFormSerializer

from bson import ObjectId

from django.contrib.auth.models import User

from tastypie import fields
from tastypie.authorization import Authorization

#from twofactor.api_auth import ApiTokenAuthentication


class DataResource( MongoDBResource ):
    id          = fields.CharField( attribute='_id' )
    survey_id   = fields.CharField( attribute='survey' )
    timestamp   = fields.DateTimeField( attribute='timestamp' )
    data        = fields.DictField( attribute='data' )

    class Meta:
        collection = 'survey_data'
        resource_name = 'data'
        object_class = Document

        list_allowed_methos     = []
        detail_allowed_methods  = [ 'get' ]

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


class BasicAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        '''
            SUPER basic authorization. Checks to see if user exists.
        '''
        try:
            return User.objects.get( username=request.GET.get( 'user', None ) ) is not None
        except:
            return False


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
