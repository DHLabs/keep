from bson import ObjectId
from datetime import datetime

from django.db import models
from django.db.models import Q

from guardian.shortcuts import assign_perm

from backend.db import db


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
        verbose_name = 'project'
        verbose_name_plural = 'projects'

    def __unicode__( self ):
        return self.name


class RepositoryManager( models.Manager ):
    def list_by_username( self, username ):
        return self.filter(Q(user__username=username) | Q(org__name=username))

    def get_by_username( self, repo_name, username ):
        return self.get( Q(name=repo_name),
                         Q(user__username=username) | Q(org__name=username) )

    def repo_exists( self, repo_name, username ):
        return self.filter(Q(name=repo_name),
                           Q(user__username=username) | Q(org__name=username))\
                   .exists()


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
            ( 'view_repository', 'View Repo' ),
            ( 'share_repository', 'Share Repo' ),

            ( 'view_data', 'View data in Repo' ),
            ( 'add_data', 'Add data to Repo' ),
            ( 'edit_data', 'Edit data in Repo' ),
            ( 'delete_data', 'Delete data from Repo' ), )

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
        else:
            super( Repository, self ).save( *args, **kwargs )

    def add_data( self, data ):
        repo_data = {
            'label': self.name,
            'repo': ObjectId( self.mongo_id ),
            'data': data,
            'timestamp': datetime.utcnow() }
        return db.data.insert( repo_data )

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