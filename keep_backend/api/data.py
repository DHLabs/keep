import pymongo

from backend.db import db
from backend.db import DataSerializer

from bson import ObjectId
from bson.code import Code

from django.conf import settings
from django.conf.urls import url
from django.http import HttpResponse

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
        detail_allowed_methods  = [ 'get','delete' ]

        authentication = MultiAuthentication( ApiTokenAuthentication(),
                                              SessionAuthentication() )

        authorization = DataAuthorization()

    def prepend_urls(self):
        base_url = '^(?P<resource_name>%s)/(?P<mongo_id>\w+)' % ( self._meta.resource_name )

        return [
            url( regex=r"%s/stats/$" % ( base_url ),
                 view=self.wrap_view( 'get_statistics' ),
                 name='api_dispatch_statistics' ),

            url( regex=r"%s/sample/$" % ( base_url ),
                 view=self.wrap_view( 'sample_data' ),
                 name='api_dispatch_data_sample' ) ]

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

    def delete_detail( self, request, **kwargs ):

        repo_id = kwargs[ 'pk' ]

        try:
            basic_bundle = self.build_bundle( request=request )
            repo = Repository.objects.get( mongo_id=repo_id )

            if not self.authorized_delete_detail( repo, basic_bundle ):
                return HttpUnauthorized()

            data_id = request.GET['data_id']

            if not data_id:
                return HttpResponse( status=404 )

            db.data.remove( { '_id': ObjectId( data_id ) } )

            return HttpResponse( status=200 )

        except Exception as e:
            return HttpBadRequest( str( e ) )

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

            if 'doctor_id' in request.GET:
                if request.GET['doctor_id'] == '':
                    query_parameters['data.aaaaa'] = 'blahblah'
                else:
                    query_parameters['data.doctor_id'] = request.GET['doctor_id']
            else:
                if request.user.username == 'AnonymousUser':
                    query_parameters['data.aaaaa'] = 'blahblah'

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

            data_serializer = DataSerializer()

            if repo.is_tracker and repo.study:
                linked = Repository.objects.filter( study=repo.study ).exclude( id=repo.id )
                data = {
                'meta': meta,
                'data': data_serializer.dehydrate( cursor.skip( offset * limit ).limit( limit ),
                                                   repo, linked ) }
            else:
                data = {
                    'meta': meta,
                    'data': data_serializer.dehydrate( cursor.skip( offset * limit ).limit( limit ),
                                                   repo ) }

            return self.create_response( request, data )
        except ValueError as e:
            return HttpBadRequest( str( e ) )

    def sample_data( self, request, **kwargs ):
        '''
            Run data sampling using the MongoDB aggregate command.
        '''

        xaxis = request.GET.get( 'x', None )
        yaxis = request.GET.get( 'y', None )

        if xaxis is None or yaxis is None:
            return HttpBadRequest( 'x and y params must be set' )

        xaxis = xaxis.split( '.' )
        yaxis = yaxis.split( '.' )

        if xaxis[0] not in [ 'data', 'timestamp', 'count' ]:
            return HttpBadRequest( 'invalid x param' )

        if yaxis[0] not in [ 'data', 'timestamp', 'count' ]:
            return HttpBadRequest( 'invalid y param' )

        x_label = '%s.%s' % ( xaxis[0], xaxis[1] )
        y_label = '%s.%s' % ( yaxis[0], yaxis[1] )

        # Create the aggregate pipeline needed to do our query
        match = { '$match': {
                    'repo': ObjectId( kwargs.get( 'mongo_id' ) ),
                    x_label: { '$exists': True },
                    y_label: { '$exists': True } } }

        project = { '$project': {
                        '_id': 0,
                        'x': '$%s.%s' % ( xaxis[0], xaxis[1] ),
                        'y': '$%s.%s' % ( yaxis[0], yaxis[1] ) } }

        sort = { '$sort': { 'x': 1 } }

        aggregate = db.data.aggregate( pipeline=[match, project, sort] )

        results = []
        for row in aggregate.get( 'result' ):
            results.append( row )

        return self.create_response( request, results )


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

        count_by_day = []
        result = db.data.map_reduce( day_map, day_reduce, "myresults", query=repo_filter )
        for doc in result.find():
            count_by_day.append( {
                'day':      doc[ '_id' ][ 'day' ],
                'value':    doc[ 'value' ][ 'count' ] })

        stats = {
            'total_count': cursor.count(),
            'count_by_day': count_by_day,
            'first_submission': first,
            'last_submission': last,
        }

        return self.create_response( request, stats )
