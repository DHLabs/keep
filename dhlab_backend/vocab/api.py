import pymongo

from backend.db import db, MongoDBResource

from tastypie import fields
from tastypie.resources import ModelResource

class VocabResource( MongoDBResource ):
	'''
		VocabResource is used to access the database,
		And query for autocomplete purposes.
	'''

	id		= fields.CharField( attribute='_id' )
	data 	= fields.CharField( attribute='data', null=True )

	class Meta:

		collection = 'vocab'
		resource_name = 'vocab'

		list_allowed_methods = [ 'get' ]

		filtering = {
			'data' : ( 'icontains', )
		}

	def build_filters ( self, filters=None ):
		if 'data__icontains' in filters:
			return super( VocabResource, self ).build_filters( filters )