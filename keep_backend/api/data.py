import pymongo

from backend.db import db
from backend.db import dehydrate_survey

from bson import ObjectId
from bson.code import Code

from django.conf import settings
from django.conf.urls import url

from tastypie import fields
from tastypie.authentication import MultiAuthentication, SessionAuthentication
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

        authentication = MultiAuthentication( ApiTokenAuthentication(),
                                              SessionAuthentication() )

        authorization = DataAuthorization()

    def prepend_urls(self):
        base_url = '^(?P<resource_name>%s)/' % ( self._meta.resource_name )
        return [
            url( regex=r"%s(?P<mongo_id>\w+)/stats/$" % ( base_url ),
                 view=self.wrap_view('get_statistics'),
                 name="api_dispatch_statistics") ]

    def _build_filters( self, request ):
        """
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
        """

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

    def _build_sort( self, request ):

        if 'sort' not in request:
            return None

        sort = {}

        sort[ 'param' ] = 'data.%s' % ( request.get('sort') )
        sort[ 'type' ] = pymongo.DESCENDING

        if 'sort_type' in request and request.get('sort_type') in [ 'asc', 'ascending' ]:
            sort[ 'type' ] = pymongo.ASCENDING

        return sort

    def _serialize_data( self, data, fields, repo_id, data_id ):

        copy = {}

        for field in fields:

            key = field.get( 'name' )
            val = data.get( key )

            # Convert strings into a unicode representation.
            if field.get( 'type' ) in [ 'text', 'note' ]:
                val = unicode( val ).encode( 'utf-8' )

            # Give a full URL for media
            elif field.get( 'type' ) in [ 'photo' ]:

                host = settings.AWS_S3_MEDIA_DOMAIN
                if settings.DEBUG:
                    host = 'localhost:8000/media'

                val = 'http://%s/%s/%s/%s' % ( host, repo_id, data_id, val )

            # Correctly recurse through groups
            elif field.get( 'type' ) == 'group':

                val = self._serialize_data( data=val,
                                            fields=field.get( 'children' ),
                                            repo_id=repo_id,
                                            data_id=data_id )

            copy[ key ] = val

        return copy


    def _dehydrate_data( self, data, fields ):

        hydrated = []
        for row in data:
            copy = dict( row )

            # Hydrate the base data keys.
            # 1. Remove the "repo" key if it exists.
            # 2. Rename the "_id" key into the more common "id" key.
            # 3. Convert the python timestamp into a JSON friendly one.
            repo = copy.pop( 'repo' )
            copy[ 'id' ] = copy.pop( '_id' )
            copy[ 'timestamp' ] = copy[ 'timestamp' ].strftime( '%Y-%m-%dT%X' )

            # Now serialize the data according to the field data.
            copy[ 'data' ] = self._serialize_data( data=copy[ 'data' ],
                                                   fields=fields,
                                                   repo_id=repo,
                                                   data_id=copy[ 'id' ] )

            hydrated.append( copy )

        return hydrated

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

            if 'bbox' in request.GET and 'geofield' in request.GET:
                # Convert the bounding box into the $box format needed to do
                # a geospatial search in MongoDB
                # http://docs.mongodb.org/manual/reference/operator/box/
                try:
                    bbox = map( float, request.GET[ 'bbox' ].split( ',' ) )
                except ValueError:
                    return HttpBadRequest( 'Invalid bounding box' )

                bbox = [ [ bbox[0], bbox[1] ], [ bbox[2], bbox[3] ] ]
                geofield = request.GET[ 'geofield' ]

                query_parameters[ 'data.%s' % ( geofield ) ] = {'$geoWithin': {'$box': bbox}}

            # Query data from MongoDB
            cursor = db.data.find( query_parameters )

            sort_params = self._build_sort( request.GET )
            if sort_params is not None:
                cursor = cursor.sort( sort_params.get( 'param' ), sort_params.get( 'type' ) )

            # Ensure correct pagination
            offset = max( int( request.GET.get( 'offset', 0 ) ), 0 )

            #
            # TODO: Smarter way of printing out entire dataset for CSVs
            # When people download CSVs, make sure we include the entire dataset.
            limit = 50
            if request.GET.get( 'format', None ) == 'csv':
                limit = cursor.count()

            # Determine the number of pages available.
            pages = 0
            if limit > 0:
                pages = cursor.count() / limit

            meta = {
                'form_name': repo.name,
                'fields': repo.flatten_fields(),
                'limit': limit,
                'offset': offset,
                'count': cursor.count(),
                'pages': pages }

            data = {
                'meta': meta,
                'data': self._dehydrate_data( cursor.skip( offset * limit ).limit( limit ),
                                              repo.fields() ) }

            return self.create_response( request, data )
        except ValueError as e:
            return HttpBadRequest( str( e ) )

    def get_statistics( self, request, **kwargs ):
        '''
            Get "statistics" aim is to (ultimately) run MapReduce functions on
            the set of data in a specific repository.
        '''
        day_map = Code( '''
            function() {
                day = Date.UTC( this.timestamp.getFullYear(), this.timestamp.getMonth(), this.timestamp.getDate() );
                emit( { day: day }, { count: 1 } )
            }''')

        day_reduce = Code( '''
            function( key, values ) {
                var count = 0;
                values.forEach( function( v ) {
                    count += v[ 'count' ];
                });
                return {count: count};
            }''')

        # Grab the survey that we're querying survey data for
        repo_filter = { 'repo': ObjectId( kwargs.get( 'mongo_id' ) ) }

        cursor = db.data.find( repo_filter )

        first = db.data.find_one( repo_filter, sort=[( '_id', pymongo.ASCENDING )] )
        last  = db.data.find_one( repo_filter, sort=[( '_id', pymongo.DESCENDING )] )

        result = db.data.map_reduce( day_map, day_reduce, "myresults", query=repo_filter )
        for doc in result.find():
            print doc

        stats = {
            'count': cursor.count(),
            'first_submission': first,
            'last_submission': last,
        }

        return self.create_response( request, stats )
