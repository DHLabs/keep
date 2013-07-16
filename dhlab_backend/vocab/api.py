import pymongo

from backend.db import db, MongoDBResource, Document
from backend.serializers import CSVSerializer

from django.http import HttpResponse

from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest
from tastypie.http import HttpNotFound, HttpUnauthorized
from tastypie.resources import ModelResource

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