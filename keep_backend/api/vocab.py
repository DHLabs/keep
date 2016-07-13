import pymongo
import re

from django.http import HttpResponse

from tastypie import fields
from tastypie.exceptions import BadRequest
from tastypie.utils.mime import build_content_type

from backend.db import db
from backend.db import dehydrate_survey

from .resources import MongoDBResource, Document
from .serializers import CSVSerializer


class VocabResource( MongoDBResource ):
    """
        VocabResource is used to access the mecical vocabulary,
        and query for autocomplete purposes.

        Parameters
        ----------
        MongoDBResource : MongoDBResource

        Attributes
        ----------
        id : string
            A string comprising of the Mongo ID.
        term : string
            A string containing the medical term.
        group : string
            Unused as of now, a string defining the medical dictionary
            the term is from.  (For KEEP, we have 'snomed' as our group)
    """

    id      = fields.CharField( attribute='_id' )
    term    = fields.CharField( attribute='term' )
    group   = fields.CharField( attribute='group' )

    class Meta:
        collection = 'vocab'
        resource_name = 'vocab'
        #authorization = Authorization()
        object_class = Document
        serializer = CSVSerializer()

        list_allowed_methods = [ 'get' ]

        include_resource_uri = False

        filtering = {
            'term': ( 'istartswith', )
        }

    def build_filters( self, filters=None ):
        """
            This API will only be used to get terms that start with
            requested string.  Require filter to be in API call.

            Parameters
            ----------
            filters : string, optional

            Returns
            -------
            String
        """
        
        if 'term__istartswith' not in filters:
            return BadRequest
        return super( VocabResource, self ).build_filters( filters )

    def create_response( self, request, data, response_class=HttpResponse, **response_kwargs ):
        '''
            This is templated from backend.api.RepoResource create_response.
        '''

        desired_format = self.determine_format(request)

        serialized = self.serialize(request, data, desired_format)
        response = response_class( content=serialized,
                                   content_type=build_content_type(desired_format),
                                   **response_kwargs )

        return response

    def get_list( self, request, **kwargs ):

        startWith = request.GET['term__istartswith']
        startRegex = re.compile( ('^' + startWith), re.IGNORECASE)
        cursor = db.vocab.find( { 'term': startRegex } )\
                         .limit( 10 )\
                         .sort( 'term', pymongo.ASCENDING )
        return self.create_response( request, dehydrate_survey( cursor ) )
