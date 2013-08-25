from django.db import models


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

    date_created = models.DateTimeField( auto_now_add=True )
    date_updated = models.DateTimeField( auto_now_add=True )

    class Meta:
        ordering = [ 'name' ]
        verbose_name = 'study'
        verbose_name_plural = 'studies'

    def owner( self ):
        if self.org:
            return self.org.name
        return self.user.name

    def __unicode__( self ):
        return self.name
