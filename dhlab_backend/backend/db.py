from bson import ObjectId

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse

from pymongo import MongoClient

from tastypie.bundle import Bundle
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized
from tastypie.resources import Resource

from twofactor.util import encrypt_value, decrypt_value

connection = MongoClient()
db = connection[ 'dhlab' ]


def dehydrate( survey ):
    for key in survey.keys():
        if isinstance( survey[ key ], ObjectId ):
            survey[ key ] = str( survey[ key ] )

    # Decrypt survey values
    if 'data' in survey:
        survey[ 'data' ] = decrypt_survey( survey[ 'data' ] )

    # Reformat python DateTime into JS DateTime
    if 'timestamp' in survey:
        survey[ 'timestamp' ] = survey[ 'timestamp' ].strftime( '%Y-%m-%dT%X' )
    return survey


def dehydrate_survey( cursor ):
    '''
        Decrypt survey data and turn any timestamps into javascript-readable
        values.
    '''
    if isinstance( cursor, dict ):
        return dehydrate( cursor )

    return [ dehydrate( row ) for row in cursor ]


def encrypt_survey( data ):
    for key in data:
        data[ key ] = encrypt_value( data[ key ] )
    return data


def decrypt_survey( data ):
    for key in data:
        data[ key ] = decrypt_value( data[ key ] )
    return data


class Document( dict ):
    # Dictionary-like object for MongoDB documents
    __getattr__ = dict.get


class MongoDBResource(Resource):
    """
    A base resource that allows to make CRUD operations for mongodb.
    """
    def get_collection(self):
        """
        Encapsulates collection name.
        """
        try:
            return db[self._meta.collection]
        except AttributeError:
            raise ImproperlyConfigured("Define a collection in your resource.")

    def obj_get_list(self, bundle, **kwargs):
        """
        Maps mongodb documents to Document class.
        """

        try:
            objects = map( Document,
                           self.authorized_read_list( self.get_collection(),
                                                      bundle ) )
        except ValueError:
            raise ImmediateHttpResponse( HttpUnauthorized() )

        return objects

    def obj_get(self, bundle, **kwargs):
        """
        Returns mongodb document from provided id.
        """

        obj = self.get_collection()\
                  .find_one( { '_id': ObjectId( kwargs.get( 'pk' ) ) } )

        try:
            if self.authorized_read_detail( obj, bundle ):
                return Document( obj )
        except ValueError:
            raise ImmediateHttpResponse( HttpUnauthorized() )

    def obj_create(self, bundle, **kwargs):
        """
        Creates mongodb document from POST data.
        """
        self.get_collection().insert(bundle.data)
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        """
        Updates mongodb document.
        """
        self.get_collection().update({
            "_id": ObjectId(kwargs.get("pk"))
        }, {
            "$set": bundle.data
        })
        return bundle

    def obj_delete(self, request=None, **kwargs):
        """
        Removes single document from collection
        """
        self.get_collection().remove({ "_id": ObjectId(kwargs.get("pk")) })

    def obj_delete_list(self, request=None, **kwargs):
        """
        Removes all documents from collection
        """
        self.get_collection().remove()

    def get_resource_uri(self, item=None):
        """
        Returns resource URI for bundle or object.
        """
        if item is None:
            return reverse( 'api_dispatch_list',
                            kwargs={
                                'api_name': 'v1',
                                'resource_name': self._meta.resource_name })

        if isinstance(item, Bundle):
            pk = item.obj._id
        else:
            pk = item._id
        return reverse( "api_dispatch_detail",
                        kwargs={
                            'api_name': 'v1',
                            'resource_name': self._meta.resource_name,
                            'pk': pk })
