import pymongo

from backend.db import db, MongoDBResource, Document

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
	data 	= fields.CharField( attribute='data' )

	class Meta:
		collection = 'vocab'
		resource_name = 'vocab'
		#authorization = Authorization()
		object_class = Document

		list_allowed_methods = [ 'get' ]

		include_resource_uri = False

		filtering = {
			'data' : 'istartswith',
		}

	#def build_filters ( self, filters=None ):
	#	if 'data__icontains' in filters:
	#		return super( VocabResource, self ).build_filters( filters )