from backend.db import db, MongoDBResource, Document
from backend.db import dehydrate_survey

from bson import ObjectId

from tastypie import fields
from tastypie.authentication import MultiAuthentication, SessionAuthentication
from tastypie.http import HttpUnauthorized

from repos.models import Repository

from .authentication import ApiTokenAuthentication
from .authorization import DataAuthorization
from .serializers import CSVSerializer


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
        detail_allowed_methods  = [ 'get', 'list' ]

        authentication = MultiAuthentication( SessionAuthentication(),
                                              ApiTokenAuthentication() )

        authorization = DataAuthorization()

    def get_detail( self, request, **kwargs ):

        # Grab the survey that we're querying survey data for
        repo_id = kwargs[ 'pk' ]

        try:
            basic_bundle = self.build_bundle( request=request )
            repo = Repository.objects.get( mongo_id=repo_id )

            if not self.authorized_read_detail( repo, basic_bundle ):
                return HttpUnauthorized()

            query_parameters = {}
            query_parameters['repo'] = ObjectId( repo_id )

            for get_parameter in request.GET:
                if "data_attr" in get_parameter:
                    the_param = get_parameter.replace("data_attr__", "")
                    query_parameters[ 'data.' + the_param ] = request.GET[ get_parameter ]

            # Query the database for the data
            cursor = db.data.find( query_parameters )

            offset = int( request.GET.get( 'offset', 0 ) )

            meta = {
                'limit': 50,
                'offset': offset,
                'count': cursor.count(),
                'pages': cursor.count() / 50
            }

            data = {
                'meta': meta,
                'data': dehydrate_survey( cursor.skip(offset * 50).limit(50)) }

            return self.create_response( request, data )
        except ValueError:
            return HttpUnauthorized()
