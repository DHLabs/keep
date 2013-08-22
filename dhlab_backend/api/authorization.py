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

    def read_detail( self, object_detail, bundle ):

        if object_detail.is_public:
            return True

        logged_in_user = bundle.request.user

        return logged_in_user.has_perm( 'view_data', object_detail )


class RepoAuthorization( Authorization ):

    def read_list( self, object_list, bundle ):

        # The user we're requesting data about
        user = bundle.request.GET.get( 'user', None )

        # Go ahead and filter for all objects by this user
        all_repos = object_list.filter( Q(user__username=user) | Q(org__name=user) )

        # Check permissions against the currently logged in user.
        filtered = []
        for repo in all_repos:
            if bundle.request.user.has_perm( 'view_repository', repo ):
                filtered.append( repo )

        return filtered

    def read_detail( self, object_detail, bundle ):

        if bundle.obj.is_public:
            return True

        logged_in_user = bundle.request.user

        return logged_in_user.has_perm( 'view_repository', bundle.obj )

    def create_detail( self, object_detail, bundle ):
        return True
