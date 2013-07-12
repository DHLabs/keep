import pymongo

from backend.db import MongoDBResource
from backend.serializers import CSVSerializer

from tastypie import fields
from tastypie.resources import ModelResource

class VocabResource( MongoDBResource ):
	'''
		VocabResource are used to access the database,
		And query for autocomplete purposes.
	'''
	id		= fields.CharField( attribute='_id' )
	data 	= fields.CharField( attribute='data', null=True )

	class Meta:
		collection = 'vocab'
		resource_name = 'vocab'
		object_class = Document
		serializer = CSVSerializer()

	def get_detail( self, request, **kwargs )
