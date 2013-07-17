import pymongo
import re

from backend.db import db, MongoDBResource, Document
from backend.db import dehydrate_survey
from backend.serializers import CSVSerializer

from bson import ObjectId

from django.http import HttpResponse

from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest
from tastypie.http import HttpNotFound, HttpUnauthorized
from tastypie.resources import ModelResource
from tastypie.utils.mime import build_content_type

class VocabResource( MongoDBResource ):
	'''
		VocabResource is used to access the database,
		And query for autocomplete purposes.
	'''

	id		= fields.CharField( attribute='_id' )
	term 	= fields.CharField( attribute='term' )

	class Meta:
		collection = 'vocab'
		resource_name = 'vocab'
		#authorization = Authorization()
		object_class = Document
		serializer = CSVSerializer()

		list_allowed_methods = [ 'get' ]

		include_resource_uri = False

		filtering = {
			'term' : ( 'istartswith', )
		}

	def build_filters ( self, filters=None ):
		'''
			This API will only be used to get terms that start with
			requested string.  Require filter to be in API call.
		'''
		if 'term__istartswith' not in filters:
			return BadRequest
		return super( VocabResource, self ).build_filters( filters )

	def create_response ( self, request, data, response_class=HttpResponse,
						  **response_kwargs ):
		'''
			This is templated from backend.api.RepoResource create_response.
		'''

		desired_format = self.determine_format(request)

		serialized = self.serialize(request, data, desired_format)
		response = response_class( content=serialized,
								   content_type=build_content_type(desired_format),
								   **response_kwargs )

		return response

	def get_list ( self, request, **kwargs ):

		startWith = request.GET['term__istartswith']
		startRegex = re.compile( ('^' + startWith), re.IGNORECASE)
		cursor = db.vocab.find( { 'term': startRegex } )\
						 .limit( 10 )\
						 .sort( 'term', pymongo.DESCENDING )
		return self.create_response( request, dehydrate_survey( cursor ) )