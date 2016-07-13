import logging

from bson import ObjectId
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.python import Serializer
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q

import random

from guardian.shortcuts import assign_perm, remove_perm, get_objects_for_user

from backend.db import db
from django.core.files.storage import default_storage as storage

from . import validate_and_format

logger = logging.getLogger( __name__ )

ALL_REPO_PERMISSIONS = [
    ( 'add_repository', 'Add Repo' ),
    ( 'delete_repository', 'Delete Repo' ),
    ( 'change_repository', 'Edit Repo' ),

    ( 'view_repository', 'View Repo' ),
    ( 'share_repository', 'Share Repo' ),

    ( 'view_data', 'View data in Repo' ),
    ( 'add_data', 'Add data to Repo' ),
    ( 'edit_data', 'Edit data in Repo' ),
    ( 'delete_data', 'Delete data from Repo' ), ]

print ("default storage is: ")
print ("in repos models")
print storage
print dir(storage)

#print dir(db)
#logger.error('testest in repos models')

#logger.info('A row is deleted successfully !!!')
class RepoSerializer( Serializer ):
    """
        Converts a QuerySet of Repository objects into a specific JSON format.
    """

    def end_object( self, obj ):
        # We want to refer to repos externally according to their mongo_id
        self._current[ 'id' ] = obj.mongo_id
        self._current.pop( 'mongo_id' )
        print "mongo_id: ", obj.mongo_id

        # Convert study id into the actual study name
        if obj.study:
            self._current[ 'study' ] = obj.study.name

        # Convert timestamps into JSON timestamps
        self._current[ 'date_updated' ] = obj.date_updated.strftime( '%Y-%m-%dT%X' )
        self._current[ 'date_created' ] = obj.date_created.strftime( '%Y-%m-%dT%X' )

        # Add reference
        self._current[ 'children' ] = obj.fields()

        # Include the number of submissions for this repo
        self._current[ 'submissions' ]  = obj.submissions()

        # Add references to webform/visualization urls
        kwargs = { 'repo_name': obj.name }
        if obj.org:
            kwargs[ 'username' ] = obj.org.name
        else:
            kwargs[ 'username' ] = obj.user.username

        self._current[ 'webform_uri' ] = reverse( 'repo_webform', kwargs=kwargs )
        self._current[ 'uri' ] = reverse( 'repo_visualize', kwargs=kwargs)

        # Set the type of the "repo"
        if obj.is_tracker:
            self._current[ 'type' ] = 'register'
        else:
            self._current[ 'type' ] = 'survey'

        # Remove references to user/org for now.
        self._current.pop( 'org' )

        self.objects.append( self._current )


class RepositoryManager( models.Manager ):

    def list_by_user( self, user, organizations=None, public=False ):
        '''
            List shared & user-owned repositories for a specific user.
        '''
        print "in repos/models RepositoryManager "
        # Grab all public repositories
        public_repos = self.filter( is_public=True )

        # django-guardian has a quirk where if the user is a superuser, the
        # entire queryset is returned. This is bullshit and we don't need that
        # bullshit.
        user.is_superuser = False
        repositories = get_objects_for_user( user,
                                             [ 'view_repository' ],
                                             self,
                                             use_groups=False,
                                             any_perm=False )

        if public:
            return repositories.filter( is_public=True )

        return repositories | public_repos

    def get_by_username( self, repo_name, username ):
        user_repo_q = Q( name=repo_name )
        user_repo_q.add( Q( user__username=username ), Q.AND )
        user_repo_q.add( Q( org=None ), Q.AND )

        org_repo_q = Q( name=repo_name )
        org_repo_q.add( Q( org__name=username ), Q.AND )

        try:
            return self.get( user_repo_q | org_repo_q )
        except ObjectDoesNotExist as e:
            return None

    def repo_exists( self, repo_name, username ):
        return self.filter(Q(name=repo_name),
                           Q(user__username=username) | Q(org__name=username))\
                   .exists()


class Relationship( models.Model ):
    """
        Represents a relationship between two repos
    """

    name        = models.CharField( max_length=256, blank=False )

    repo_parent = models.ForeignKey( 'repos.Repository',
                                     related_name='parent_relations',
                                     blank=False )

    repo_child  = models.ForeignKey( 'repos.Repository',
                                     related_name='child_relations',
                                     blank=False )

    class Meta:
        ordering = [ 'name' ]
        verbose_name = 'relationship'
        verbose_name_plural = 'relationships'


class Repository( models.Model ):
    """
        Represents a data repository.

        Fields
        -------
        mongo_id : string : required
            Reference to the MongoDB ID.

        name : string : required
            Name only has to be unique for a user's list of repositories.

        study : id : optional
            Study this repository belongs too.

        user : id : required
            User in which this repository belongs too.

        org : id : required
            Organization in which this repository belongs too.

        is_tracker : boolean: required, default=False
            Whether this repository is being used to track items in a study.

        is_public : boolean : required, default=False
            Whether this everything in this repository is public/private.

        is_form_public : boolean : required, default=False
            Whether the form for this repository is public/private.

        description : string : optional
            Description of the repository.

        date_created : timestamp : auto
        date_uploaded : timestamp : auto
            Datetime that the repository was created.
    """

    objects     = RepositoryManager()

    mongo_id    = models.CharField( max_length=24,
                                    blank=False )

    name        = models.CharField( max_length=256,
                                    blank=False )

    study       = models.ForeignKey( 'studies.Study',
                                     related_name='repositories',
                                     null=True )

    user         = models.ForeignKey( 'auth.User',
                                      related_name='repositories',
                                      null=True )

    org          = models.ForeignKey( 'organizations.Organization',
                                      related_name='repositories',
                                      null=True )

    is_tracker      = models.BooleanField( default=False )

    is_public       = models.BooleanField( default=False )
    is_form_public  = models.BooleanField( default=False )

    description = models.CharField( max_length=1024, blank=True )

    date_created = models.DateTimeField( auto_now_add=True )
    date_updated = models.DateTimeField( auto_now_add=True )

    class Meta:
        ordering = [ 'org', 'name' ]
        verbose_name = 'repository'
        verbose_name_plural = 'repositories'

        # Additional permissions on top of the original add, delete, change
        # repo permissions
        permissions = (
            ( 'view_repository', 'View Repo' ),
            ( 'share_repository', 'Share Repo' ),

            ( 'view_data', 'View data in Repo' ),
            ( 'add_data', 'Add data to Repo' ),
            ( 'edit_data', 'Edit data in Repo' ),
            ( 'delete_data', 'Delete data from Repo' ), )

    def _flatten( self, fields, include_group ):
        '''
            Returns a flat list of fields.
        '''
        field_list = []

        for field in fields:
            if 'group' in field.get( 'type' ):
                if include_group:
                    field_list.append( field )
                field_list.extend( self._flatten( field.get( 'children' ), include_group ) )
                continue

            field_list.append( field )
        print " in repos/models flatten: "

        return field_list

    def delete( self ):
        """
            Delete all data & objects related to this object
        """
        print "in repos/models delete "
        # Remove related data from MongoDB
        db.repo.remove( { '_id': ObjectId( self.mongo_id ) } )
        db.data.remove( { 'repo': ObjectId( self.mongo_id ) } )

        # Finally remove the repo metadata ifself
        super( Repository, self ).delete()

    def move_to( self, new_user, new_org=None ):
        # Remove all permissions from the current user and assign it to the new
        # user.
        for perm in ALL_REPO_PERMISSIONS:
            remove_perm( perm[0], self.user, self )
            assign_perm( perm[0], new_user, self )

            if self.org:
                remove_perm( perm[0], self.org, self )

            if new_org is not None:
                assign_perm( perm[0], new_org, self )

        self.user = new_user
        self.org  = new_org

    def save( self, *args, **kwargs ):
        # Only add repo object to MongoDB on a object creation
        if self.pk is None:
            if len( self.mongo_id ) == 0:
                repo = kwargs.pop( 'repo', None )
                # Save repo field data to MongoDB and save repo metadata to a
                # relational database
                
                self.mongo_id = db.repo.insert( repo )

            super( Repository, self ).save( *args, **kwargs )

            # As the owner of this repo we have full permissions!
            for perm in ALL_REPO_PERMISSIONS:
                assign_perm( perm[0], self.user, self )

                if self.org:
                    assign_perm( perm[0], self.org, self )
        
        else:
            super( Repository, self ).save( *args, **kwargs )
        print "in repos/models save for object creation "

    def data( self ):
        '''
            Does a simple query for data.
        '''
        return db.data.find( { 'repo': ObjectId( self.mongo_id ) } )

    def update_data( self, data, files ):
        """
            Validate and update data record with new data
        """
        #TODO: maybe remove old files??
        
        fields = self.fields()
        print "in repos/models update_data for ", self.fields()
        validated_data, valid_files = validate_and_format(fields, data, files)

        db.data.update( {"_id":ObjectId( data['detail_data_id'] )},{"$set": { 'data': validated_data, 'timestamp':datetime.utcnow() }} )

        # Once we save the repo data, save the files to S3
        if len( valid_files.keys() ) > 0:
            # If we have media data, save it to this repo's data folder
            if not settings.DEBUG:
                storage.bucket_name = settings.AWS_MEDIA_STORAGE_BUCKET_NAME
            for key in valid_files.keys():

                file_to_upload = valid_files.get( key )

                s3_url = '%s/%s/%s' % ( self.mongo_id,
                                        new_data_id,
                                        file_to_upload.name )
		print ("in repos/models update_data going to store in s3")
		print s3_url, file_to_upload
                storage.save( s3_url, file_to_upload )

		

    def add_data( self, data, files ):
        """
            Validate and add a new data record to this repo!
        """
        print " in repos/add_data "
        fields = self.fields()
        validated_data, valid_files = validate_and_format(fields, data, files)

        # Ensure tracker id's are unique
        if self.is_tracker:
            while True:
                validated_data[self.study.tracker] = str(random.randrange(100000000,999999999))

                if db.data.find( { "data.{0}".format(self.study.tracker): validated_data[self.study.tracker] } ).count() == 0:
                    break

        repo_data = {
            'label': self.name,
            'repo': ObjectId( self.mongo_id ),
            'data': validated_data,
            'timestamp': datetime.utcnow() }

        logger.info( repo_data )

        new_data_id = db.data.insert( repo_data )

        # Once we save the repo data, save the files to S3
        if len( valid_files.keys() ) > 0:
            # If we have media data, save it to this repo's data folder
            if not settings.DEBUG:
                storage.bucket_name = settings.AWS_MEDIA_STORAGE_BUCKET_NAME
            for key in valid_files.keys():

                file_to_upload = valid_files.get( key )

                s3_url = '%s/%s/%s' % ( self.mongo_id,
                                        new_data_id,
                                        file_to_upload.name )
		print ("in repos/models add_datat going to store in s3 ")
		
                storage.save( s3_url, file_to_upload )

        return new_data_id

    def add_task( self, task_id, task_type ):
        '''
            Track of tasks id ( and subsequently their results ) on a per repo
            basis.

            Params
            ------
            task_id : integer
                Task id returned by Celery
            task_type : string
                An identifier for this task. ( i.e "csv_upload", etc )
        '''
        task_data = {
            'repo': ObjectId( self.mongo_id ),
            'task': task_id,
            'type': task_type }

        task_id = db.task.insert( task_data )
        return task_id

    # If repo is part of a study, and that study has a tracker repo, returns that repo
    def registry( self ):
        if self.is_tracker:
            return self
        elif self.study:
            study_repos = Repository.objects.filter(study=self.study).filter(is_tracker=True)
            if study_repos:
                return study_repos[0]
        return None

    def remove_task( self, task_id ):
        return db.task.remove( { 'task': task_id } )

    def flatten_fields( self ):
        return self._flatten( self.fields(), False )

    def flatten_fields_with_group( self ):
        return self._flatten( self.fields(), True )

    def fields( self ):
        return db.repo.find_one( ObjectId( self.mongo_id ) )[ 'fields' ]

    def update_fields( self, fields ):
        db.repo.update( { '_id': ObjectId( self.mongo_id ) },
                        { '$set': { 'fields': fields } } )

    def submissions( self ):
        return db.data.find({ 'repo': ObjectId( self.mongo_id ) } ).count()

    def tasks( self ):
        return db.task.find( { 'repo': ObjectId( self.mongo_id ) } )

    def owner( self ):
        if self.org:
            return self.org.name
        return self.user.username

    def __unicode__( self ):
        return '<Repository %s/%s>' % ( self.owner(), self.name )
