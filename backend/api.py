from backend.db import MongoDBResource, Document

from tastypie import fields

from twofactor.api_auth import ApiTokenAuthentication


class FormResource( MongoDBResource ):
    id          = fields.CharField( attribute='_id' )
    name        = fields.CharField( attribute='name', null=True )
    children    = fields.ListField( attribute='children', null=True )

    class Meta:
        resource_name = 'forms'
        authentication = ApiTokenAuthentication()
        object_class = Document
        collection = 'survey'
