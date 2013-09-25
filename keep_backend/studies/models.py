from django.core.serializers.python import Serializer
from django.db import models


class StudySerializer( Serializer ):
    '''
        Converts a QuerySet of Study objects into a specific JSON format.
    '''
    def end_object( self, obj ):
        # Convert timestamps into JSON timestamps
        self._current[ 'date_updated' ] = obj.date_updated.strftime( '%Y-%m-%dT%X' )
        self._current[ 'date_created' ] = obj.date_created.strftime( '%Y-%m-%dT%X' )

        self._current[ 'id' ] = obj.id

        self._current.pop( 'user' )
        self._current.pop( 'org' )

        self.objects.append( self._current )


class Study( models.Model ):
    '''
        Represents a "study" aka group of repository. A study is a purely
        grouping concept.

        Fields
        ------
        name : string
            Name only has to be unique for a user's list of studies.

        user : id
            ID reference to user which created this study.

        org : id
            ID reference to organization which created this study.

        description : string : optional
            Description of the study.

        tracker : string : optional
            Field name that is used ( and automatically entered into new repos )
            across all repos in this study to track certain objects.

        date_created : timestamp : auto
        date_updated : timestamp : auto
    '''

    name        = models.CharField( max_length=256, blank=False )

    user        = models.ForeignKey( 'auth.User',
                                     related_name='studies',
                                     null=True )

    org         = models.ForeignKey( 'organizations.Organization',
                                     related_name='studies',
                                     null=True )

    description = models.CharField( max_length=1024, blank=True )

    tracker     = models.CharField( max_length=256, blank=True )

    date_created = models.DateTimeField( auto_now_add=True )
    date_updated = models.DateTimeField( auto_now_add=True )

    class Meta:
        ordering = [ 'name' ]
        verbose_name = 'study'
        verbose_name_plural = 'studies'

    def delete( self ):
        '''
            If we have a bunch of repos attached to a study, delete them all
            as well.
        '''
        study_repos = self.repositories.all()
        if len( study_repos ) > 0:
            for repo in study_repos:
                repo.delete()

        super( Study, self, ).delete()

    def owner( self ):
        if self.org:
            return self.org.name
        return self.user.name

    def __unicode__( self ):
        return self.name
