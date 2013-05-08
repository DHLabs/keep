import hashlib

from django.db import models

USER_MODEL = 'auth.User'


class Organization( models.Model ):
    '''
        Umbrella object with which users are associated.

        An organization can have multiple users.
    '''
    name = models.CharField( max_length=200,
                             unique=True,
                             help_text='The name of the organization' )

    gravatar = models.EmailField( blank=True )
    owner = models.ForeignKey( USER_MODEL )
    users = models.ManyToManyField( USER_MODEL,
                                    through='OrganizationUser',
                                    related_name='organization_users' )

    class Meta:
        ordering = [ 'name' ]
        verbose_name = 'organization'
        verbose_name_plural = 'organizations'

    def __unicode__( self ):
        return self.name

    def icon( self ):
        if len( self.gravatar ) == 0:
            return '//gravatar.com/avatar/0000000000000000000000000000000?d=mm'

        m = hashlib.md5()
        m.update( self.gravatar.strip().lower() )
        return '//gravatar.com/avatar/%s' % ( m.hexdigest() )

    @staticmethod
    def has_user( org, user ):
        if isinstance( org, Organization ):
            org_user = OrganizationUser.objects.filter( user=user,
                                                        organization=org )
        else:
            organization = Organization.objects.get( id=org )
            org_user = OrganizationUser.objects.filter( user=user,
                                                        organization=organization )
        return len( org_user ) > 0


class OrganizationUser( models.Model ):
    '''
        ManyToMany through field relating Users to Organizations

        Since it is possible for a User to be a member of multiple orgs this
        class relates the OrganizationUser ot the User model using a ForeignKey
        relationship, rather than a OneToOne relationship.
    '''
    user = models.ForeignKey( USER_MODEL,
                              related_name='organization_user' )
    organization = models.ForeignKey( Organization,
                                      related_name='organization_user' )
    is_admin = models.BooleanField( default=False )

    class Meta:
        ordering = [ 'organization', 'user' ]
        unique_together = ( 'user', 'organization' )
        verbose_name = 'organization user'
        verbose_name_plural = 'organization users'

    def __unicode__( self ):
        return '%s ( %s )' % ( self.user.email, self.organization.name )
