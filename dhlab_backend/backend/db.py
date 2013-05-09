from bson import ObjectId
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse

from pymongo import MongoClient

from tastypie.bundle import Bundle
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized
from tastypie.resources import Resource

from organizations.models import Organization, OrganizationUser

connection = MongoClient( settings.MONGODB_HOST, settings.MONGODB_PORT )
db = connection[ settings.MONGODB_DBNAME ]


def dehydrate( survey ):
    for key in survey.keys():
        if isinstance( survey[ key ], ObjectId ):
            survey[ key ] = str( survey[ key ] )

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


def user_or_organization( name ):
    results = User.objects.filter( username=name )

    if len( results ) > 0:
        return results[0]

    results = Organization.objects.filter( name=name )

    if len( results ) > 0:
        return results[0]

    return None


class Repository( object ):
    objects = db.survey

    @staticmethod
    def delete( repo ):
        '''
            Deletes a repository and all the data associated with it.

            Assumes the correct permission checks have already been done.
        '''
        db.survey.remove( { '_id': repo[ '_id' ] } )
        db.data.remove( { 'repo': repo[ '_id' ] } )

    @staticmethod
    def add_data( repo, data, account ):
        # The validated & formatted survey data.
        repo_data = { 'data': data }

        if isinstance( account, User ):
            repo_data[ 'user' ] = account.id
        elif isinstance( account, Organization ):
            repo_data[ 'org' ] = account.id

        # Survey/form ID associated with this data
        repo_data[ 'repo' ] = repo[ '_id' ]

        # Survey name (used for feed purposes)
        repo_data[ 'survey_label' ] = repo[ 'name' ]

        # Timestamp of when this submission was received
        repo_data[ 'timestamp' ] = datetime.utcnow()

        return db.data.insert( repo_data )

    @staticmethod
    def permissions( repo, user ):
        '''
            Determine whether this <account> has permission to view the <repo>.
        '''
        permissions = set([])

        # Is this repo public?
        if repo.get( 'public', False ):
            permissions.add( 'view' )

        if 'user' in repo:
            # Is this user the owner of the repo?
            if repo[ 'user' ] == user.id:
                permissions.add( 'view' )
                permissions.add( 'view_raw' )
                permissions.add( 'delete' )

        elif 'org' in repo:
            org = Organization.objects.get( id=repo[ 'org' ] )

            # Is this user the owner of this org?
            if org.owner == user:
                permissions.add( 'view' )
                permissions.add( 'view_raw' )
                permissions.add( 'delete' )
            # Is this user a member of this organization
            elif Organization.has_user( user ):
                permissions.add( 'view' )
                permissions.add( 'view_raw' )

        return permissions

    @staticmethod
    def get_repo( name, account ):
        '''
            Find a repository based on the repository name and a <User> or
            <Organization> account.
        '''
        query = { 'name': name }

        if isinstance( account, Organization ):
            query[ 'org' ] = account.id
        else:
            query[ 'user' ] = account.id

        return Repository.objects.find_one( query )

    @staticmethod
    def list_repos( account, **kwargs ):
        '''
            Return a list of repositories for a specific <account>
        '''
        query = { 'user': account.id }

        for key in kwargs:
            query[ key ] = kwargs.get( key )

        cursor = db.survey.find( query )

        repos = []
        for repo in cursor:
            repo[ 'mongo_id' ] = repo[ '_id' ]

            query = { 'repo': ObjectId( repo[ '_id' ] ) }
            repo[ 'submission_count' ] = db.data.find( query ).count()

            del repo[ '_id' ]
            repos.append( repo )

        return repos

    @staticmethod
    def shared_repos( account, **kwargs ):
        '''
            Return a list of shared repositories for a specifc <account>
        '''
        orgs = OrganizationUser.objects.filter( user=account,
                                                pending=False )

        # Map org id to org name
        org_map = {}
        for org in orgs:
            org_map[ org.organization.id ] = org.organization.name

        query = { 'org': { '$in': [ org.organization.id for org in orgs ] } }
        cursor = db.survey.find( query )

        repos = []
        for repo in cursor:
            repo[ 'mongo_id' ] = repo[ '_id' ]
            repo[ 'org' ] = org_map[ repo[ 'org' ] ]

            query = { 'repo': ObjectId( repo[ '_id' ] ) }
            repo[ 'submission_count' ] = db.data.find( query ).count()

            del repo[ '_id' ]
            repos.append( repo )

        return repos


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
