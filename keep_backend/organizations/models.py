import hashlib

from django.contrib.auth.models import Group
from django.db import models

USER_MODEL = 'auth.User'


class Organization( Group ):
    '''
        Umbrella object with which users are associated.

        An organization can have multiple users.
    '''
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

    def add_user( self, user ):
        '''
            Add a ( pending ) user to this organization.
        '''
        pending_user = OrganizationUser( user=user,
                                         organization=self,
                                         pending=True,
                                         is_admin=False )
        pending_user.save()
        return pending_user

    def has_user( self, user ):
        org_user = OrganizationUser.objects.filter( user=user,
                                                    organization=self )
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
    pending  = models.BooleanField( default=True )
    is_admin = models.BooleanField( default=False )

    class Meta:
        ordering = [ 'organization', 'user' ]
        unique_together = ( 'user', 'organization' )
        verbose_name = 'organization user'
        verbose_name_plural = 'organization users'

    def __unicode__( self ):
        return '%s ( %s )' % ( self.user.username, self.organization.name )
