from backend.db import user_or_organization

from django.contrib.auth.models import AnonymousUser, User
from django.db.models import Q

from tastypie.authorization import Authorization


class DataAuthorization( Authorization ):
    '''
        DataAuthorization determines whether a specified user can access a set
        of data from a repository.
    '''

    def read_detail( self, object_detail, bundle ):

        logged_in_user = bundle.request.user
        user = bundle.request.GET.get( 'user', None )

        if object_detail.is_public:
            return True

        # Case 1: There is no logged in user and no user query provided. We don't
        # know what to query
        if logged_in_user.is_anonymous() and user is None:
            return False

        # Case 2: There *is* a logged in user and no user query. Query repos
        # that only belong to the currently logged in user
        if user is None and logged_in_user.is_authenticated():
            public = AnonymousUser()
            return public.has_perm( 'view_data', object_detail ) or logged_in_user.has_perm( 'view_data', object_detail )

        # Case 3: User query is provided. Check whether the public or the user has access
        # to this data.
        if user is not None:
            public = AnonymousUser()
            user   = User.objects.get( username=user )
            return public.has_perm( 'view_data, object_detail' ) or user.has_perm( 'view_data', object_detail )

        return False

    def delete_detail( self, object_detail, bundle ):
        #TODO: finish this
        return True

    def put_detail( self, object_detail, bundle ):
        #TODO: finish this
        return True

class RepoAuthorization( Authorization ):

    def read_list( self, object_list, bundle ):

        logged_in_user = bundle.request.user
        user = bundle.request.GET.get( 'user', None )
        key  = bundle.request.GET.get( 'key', None )

        # A user query is provided and this is not an API call. Only
        # show public repositories for this user or repos that are shared to
        # the logged in user.
        if user is not None and key is None:

            # Check permissions against the currently logged in user.
            filtered = []
            for repo in object_list:
                if repo.is_public or repo.is_form_public or logged_in_user.has_perm( 'view_repository', repo ):
                    filtered.append( repo )

            return filtered

        return object_list

    def read_detail( self, object_detail, bundle ):

        if bundle.obj.is_public or bundle.obj.is_form_public:
            return True

        logged_in_user = bundle.request.user
        user = bundle.request.GET.get( 'user', None )
        key  = bundle.request.GET.get( 'key', None )

        if key is None:
            return logged_in_user.has_perm( 'view_repository', bundle.obj )
        else:
            user = User.objects.get( username=user )
            return user.has_perm( 'view_repository', bundle.obj )

    def create_detail( self, object_detail, bundle ):

        logged_in_user = bundle.request.user
        user = bundle.request.POST.get( 'user', None )
        key  = bundle.request.POST.get( 'key', None )

        # Case 1: No user query & the user is not logged in?
        if user is None and logged_in_user.is_anonymous():
            return False

        # Case 2: Session call. Check if the specified user has permission to
        # add data to this repo.
        if user is None and logged_in_user.is_authenticated():
            return logged_in_user.has_perm( 'add_data', object_detail )

        # Case 3: API call. Check if the specified user has permission to add
        # data to this repo
        if user is not None and key is not None:
            user = user_or_organization( user )
            return user.has_perm( 'add_data', object_detail )

        return False

    def create_list( self, object_list, bundle ):

        logged_in_user = bundle.request.user
        user = bundle.request.POST.get( 'user', None )
        key  = bundle.request.POST.get( 'key', None )

        # Case 1: There is no logged in user and no user query provided. We don't
        # know what to do.
        if user is None and logged_in_user.is_anonymous():
            return False

        # Case 2: There *is* a logged in user and no user query. Query repos
        # that only belong to the currently logged in user
        if logged_in_user.is_authenticated():
            return True

        # Case 3: A user query is provided and this is not an API call. Only
        # show public repositories for this user or repos that are shared to
        # the logged in user.
        if user is not None and key is None:
            return False

        # Case 4: API call. The object list should already be correct.
        if user is not None and key is not None:
            return True

class VizAuthorization( Authorization ):

    def read_list( self, object_list, bundle ):
        return object_list

    def read_detail( self, object_detail, bundle ):
        return True

    def create_detail( self, object_detail, bundle ):
        return True

    def delete_detail( self, object_detail, bundle ):
        return True
