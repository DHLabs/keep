import pymongo

from django.contrib.auth.models import User
from django.db.models import Q
from tastypie.authorization import Authorization
from guardian.shortcuts import get_perms

from backend.db import user_or_organization


class DataAuthorization( Authorization ):
    '''
        DataAuthorization determines whether a specified user can access a set
        of data from a repository.
    '''

    def read_list( self, object_list, bundle ):

        user = bundle.request.GET.get( 'user', None )

        account = user_or_organization( user )
        if account is None:
            raise ValueError

        query = {}
        if isinstance( account, User ):
            query[ 'user' ] = account.id
        else:
            query[ 'org' ] = account.d

        return object_list.find( query,
                                 {'data': False, 'user': False, 'org': False})\
                          .limit( 5 )\
                          .sort( 'timestamp', pymongo.DESCENDING )

    def read_detail( self, object_detail, bundle ):
        if object_detail.is_public:
            return True

        user = bundle.request.GET.get( 'user', None )
        account = user_or_organization( user )

        if account is None:
            return False

        result = account.has_perm( 'view_data', object_detail )
        if not result:
            for org in account.organization_users.all():
                if 'view_data' in get_perms( org, object_detail ):
                    return True
        else:
            return True
        return False


class RepoAuthorization( Authorization ):

    def read_list( self, object_list, bundle ):
        user = bundle.request.GET.get( 'user', None )

        account = user_or_organization( user )
        if account is None:
            raise ValueError

        return object_list.filter( Q(user__username=user) | Q(org__name=user) )

    def read_detail( self, object_detail, bundle ):

        if bundle.obj.is_public:
            return True

        account = bundle.request.GET.get( 'user', None )
        account = user_or_organization( account )
        if account is None:
            return False

        result = account.has_perm( 'view_repository', bundle.obj )
        if not result:
            for org in account.organization_users.all():
                if 'view_repository' in get_perms( org, bundle.obj ):
                    return True
        else:
            return True

        return False

    def create_detail( self, object_detail, bundle ):
        return True
