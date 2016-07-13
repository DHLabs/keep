from backend.db import db

from bson import ObjectId

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse

from tastypie.bundle import Bundle
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized
from tastypie.resources import Resource

from django.http import HttpResponse


class Document( dict ):
    # Dictionary-like object for MongoDB documents
    __getattr__ = dict.get


class MongoDBResource(Resource):
    """
    A base resource that allows to make CRUD operations for mongodb.
    """
    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
	print ("in MongoDBResource in api/resources.py")
        response = super(MongoDBResource, self).create_response(request, data)
        desired_format = self.determine_format(request)
        if desired_format == 'text/csv':
            response['Content-Disposition'] = 'inline; filename="%s.csv"' % (data['meta']['form_name'])
        return response

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
