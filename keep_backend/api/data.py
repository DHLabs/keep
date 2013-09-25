from backend.db import db
from backend.db import dehydrate_survey

from bson import ObjectId

import pymongo

from tastypie import fields
from tastypie.authentication import MultiAuthentication, SessionAuthentication, Authentication
from tastypie.http import HttpUnauthorized, HttpBadRequest

from repos.models import Repository

from .authentication import ApiTokenAuthentication
from .authorization import DataAuthorization
from .resources import MongoDBResource, Document
from .serializers import CSVSerializer

FILTER_PREFIX = 'filter'
DATA_FILTER_PREFIX = 'data'
PREFIXES = [ FILTER_PREFIX, DATA_FILTER_PREFIX ]


class DataResource( MongoDBResource ):
    id           = fields.CharField( attribute='_id' )
    repo_id      = fields.CharField( attribute='repo' )
    survey_label = fields.CharField( attribute='survey_label', null=True )
    timestamp    = fields.DateTimeField( attribute='timestamp' )
    data         = fields.DictField( attribute='data', null=True )

    class Meta:
        collection = 'data'
        resource_name = 'data'
        object_class = Document
        serializer = CSVSerializer()

        list_allowed_methos     = []
        detail_allowed_methods  = [ 'get' ]

        authentication = Authentication()

        # authentication = MultiAuthentication( SessionAuthentication(),
        #                                       ApiTokenAuthentication() )

        authorization = DataAuthorization()

    def _build_filters( self, request ):
        '''
            Build filters based on request parameters. Filters are formatted as
            follows:

            PREFIX __ KEY = VALUE or
            PREFIX __ KEY __ RELATION = VALUE

            For the data resource, the prefix can either be 'filter' or 'data'.
            A basic 'filter' prefix only looks at the top level meta-data for
            a piece of survey data. The 'data' prefix looks into the actual
            survey data itself.

            Params
            ------
            request : HttpRequest
        '''

        filters = {}
        for param in request.GET:

            # Split the parameter into the possible PREFIX/KEY/RELATION tokens.
            values = param.split( '__' )

            # Not a filter param? Skip to the next parameter
            if values[0] not in PREFIXES:
                continue

            key = values[1]
            value = request.GET[ param ]

            # Ensure we go a level deeper for the 'data' prefix
            if DATA_FILTER_PREFIX == values[0]:
                key = 'data.%s' % ( key )

            # Handle relations. No relation token is assumed to mean we want
            # an exact match.
            if len( values ) == 2:
                filters[ key ] = value
            else:
                if values[2] == 'gt':
                    filters[ key ] = { '$gt': value }
                elif value[2] == 'lt':
                    filters[ key ] = { '$lt': value }

        return filters

    def get_detail( self, request, **kwargs ):

        # Grab the survey that we're querying survey data for
        repo_id = kwargs[ 'pk' ]

        try:
            basic_bundle = self.build_bundle( request=request )
            repo = Repository.objects.get( mongo_id=repo_id )

            if not self.authorized_read_detail( repo, basic_bundle ):
                return HttpUnauthorized()

            query_parameters = self._build_filters( request )
            query_parameters['repo'] = ObjectId( repo_id )

            # Query the database for the data
            cursor = db.data.find( query_parameters )

            if 'sort' in request.GET:
                sort_parameter = 'data.%s' % ( request.GET['sort'] )
                sort_type = pymongo.DESCENDING
                if 'sort_type' in request.GET:
                    if request.GET['sort_type'] == 'ascending':
                        sort_type = pymongo.ASCENDING
                cursor = cursor.sort( sort_parameter, sort_type )

            offset = max( int( request.GET.get( 'offset', 0 ) ), 0 )

            limit = 50
            if request.GET.get( 'format', None ) == 'csv':
                limit = cursor.count()

            meta = {
                'form_name': repo.name,
                'fields': repo.flatten_fields(),
                'limit': limit,
                'offset': offset,
                'count': cursor.count(),
                'pages': cursor.count() / limit
            }

            data = {
                'meta': meta,
                'data': dehydrate_survey( cursor.skip( offset * limit ).limit( limit ) ) }

            return self.create_response( request, data )
        except ValueError as e:
            return HttpBadRequest( e )

