from bson import ObjectId
from datetime import datetime

from django.db import models
from django.db.models import Q

from guardian.shortcuts import assign_perm

from backend.db import db
from django.core.files.storage import default_storage as storage

from . import validate_and_format


class Notebook( models.Model ):
    '''
        Represents a group of repositories
    '''
    name        = models.CharField( max_length=256,
                                    blank=False )

    user         = models.ForeignKey( 'auth.User',
                                      related_name='studies',
                                      null=True )

    org          = models.ForeignKey( 'organizations.Organization',
                                      related_name='studies',
                                      null=True )

    description  = models.CharField( max_length=1024,
                                     blank=True )

    date_created = models.DateTimeField( auto_now_add=True )
    date_updated = models.DateTimeField( auto_now_add=True )

    class Meta:
        ordering = [ 'name' ]
        verbose_name = 'notebook'
        verbose_name_plural = 'notebooks'

    def __unicode__( self ):
        return self.name


class RepositoryManager( models.Manager ):
    def list_by_username( self, username ):
        return self.filter(Q(user__username=username) | Q(org__name=username))

    def get_by_username( self, repo_name, username ):
        user_repo_q = Q( name=repo_name )
        user_repo_q.add( Q( user__username=username ), Q.AND )
        user_repo_q.add( Q( org=None ), Q.AND )

        org_repo_q = Q( name=repo_name )
        org_repo_q.add( Q( org__name=username ), Q.AND )

        return self.get( user_repo_q | org_repo_q )

    def repo_exists( self, repo_name, username ):
        return self.filter(Q(name=repo_name),
                           Q(user__username=username) | Q(org__name=username))\
                   .exists()


class Relationship( models.Model ):
    '''
        Represents a relationship between two repos
    '''
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
    '''
        Represents a data repository.

        Fields
        -------
        mongo_id - required
            Reference to the MongoDB ID

        name - required
            Name only has to be unique for a user's list of repositories.

        user - required
            User in which this repository belongs too

        is_public - required, default=False
            Whether this repository is public/private

        description - optional
            Description of the repository

        date_uploaded - auto
            Datetime that the repository was created
    '''
    objects     = RepositoryManager()

    mongo_id    = models.CharField( max_length=24,
                                    blank=False )

    name        = models.CharField( max_length=256,
                                    blank=False )

    user         = models.ForeignKey( 'auth.User',
                                      related_name='repositories',
                                      null=True )

    org          = models.ForeignKey( 'organizations.Organization',
                                      related_name='repositories',
                                      null=True )

    is_public   = models.BooleanField( default=False )

    description = models.CharField( max_length=1024,
                                    blank=True )

    date_created = models.DateTimeField( auto_now_add=True )
    date_updated = models.DateTimeField( auto_now_add=True )

    class Meta:
        ordering = [ 'org', 'name' ]
        verbose_name = 'repository'
        verbose_name_plural = 'repositories'

        permissions = (
            ( 'add_repository', 'Add Repo' ),
            ( 'delete_repository', 'Delete Repo' ),
            ( 'change_repository', 'Edit Repo' ),
            ( 'view_repository', 'View Repo' ),
            ( 'share_repository', 'Share Repo' ),

            ( 'view_data', 'View data in Repo' ),
            ( 'add_data', 'Add data to Repo' ),
            ( 'edit_data', 'Edit data in Repo' ),
            ( 'delete_data', 'Delete data from Repo' ), )

        ###def update(self, fields):
        # repo = db.repo.find_one( ObjectId( self.mongo_id ) )
        # print "updating repo:"
        # print repo
        #repo[fields] = fields
    #db.repo.update( {"_id",ObjectId( self.mongo_id )},{"$set": {'fields': fields}} )

    def delete( self ):
        '''
            Delete all data & objects related to this object
        '''
        # Remove related data from MongoDB
        db.repo.remove( { '_id': ObjectId( self.mongo_id ) } )
        db.data.remove( { 'repo': ObjectId( self.mongo_id ) } )

        # Finally remove the repo metadata ifself
        super( Repository, self ).delete()

    def save( self, *args, **kwargs ):
        # Only add repo object to MongoDB on a object creation
        if self.pk is None:
            repo = kwargs.pop( 'repo', None )
            # Save repo field data to MongoDB and save repo metadata to a
            # relational database
            self.mongo_id = db.repo.insert( repo )

            super( Repository, self ).save( *args, **kwargs )

            # As the owner of this repo we have full permissions!
            for perm in self._meta.permissions:
                assign_perm( perm[0], self.user, self )

                if self.org:
                    assign_perm( perm[0], self.org, self )
        else:
            super( Repository, self ).save( *args, **kwargs )

    def add_data( self, data, files ):
        '''
            Validate and add a new data record to this repo!
        '''
        fields = self.fields()
        validated_data, valid_files = validate_and_format(fields, data, files)

        repo_data = {
            'label': self.name,
            'repo': ObjectId( self.mongo_id ),
            'data': validated_data,
            'timestamp': datetime.utcnow() }

        new_data_id = db.data.insert( repo_data )

        # Once we save the repo data, save the files to S3
        if len( valid_files.keys() ) > 0:
            # If we have media data, save it to this repo's data folder
            storage.bucket_name = 'keep-media'
            for key in valid_files.keys():

                file_to_upload = valid_files.get( key )

                s3_url = '%s/%s/%s' % ( self.mongo_id,
                                        new_data_id,
                                        file_to_upload.name )

                storage.save( s3_url, file_to_upload )

        return new_data_id

    def fields( self ):
        return db.repo.find_one( ObjectId( self.mongo_id ) )[ 'fields' ]

    def submissions( self ):
        return db.data.find({ 'repo': ObjectId( self.mongo_id ) } ).count()

    def owner( self ):
        if self.org:
            return self.org.name
        return self.user.name

    def __unicode__( self ):
        return '<Repository %s>' % ( self.name )
