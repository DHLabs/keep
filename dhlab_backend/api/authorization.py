from django.db.models import Q
from tastypie.authorization import Authorization


class DataAuthorization( Authorization ):
    '''
        DataAuthorization determines whether a specified user can access a set
        of data from a repository.
    '''

    def read_detail( self, object_detail, bundle ):

        logged_in_user = bundle.request.user

        if logged_in_user.is_anonymous():
            return object_detail.is_public

        if logged_in_user.is_authenticated():
            return logged_in_user.has_perm( 'view_data', object_detail )


class RepoAuthorization( Authorization ):

    def read_list( self, object_list, bundle ):

        logged_in_user = bundle.request.user
        user = bundle.request.GET.get( 'user', None )

        # Case 1: There is no logged in user and no user query provided. We don't
        # know what to query.
        if user is None and logged_in_user.is_anonymous():
            return False

        # Case 2: There *is* a logged in user and no user query. Query repos
        # that only belong to the currently logged in user
        if user is None and logged_in_user.is_authenticated():
            return object_list.filter( user=logged_in_user )

        # Case 3: A user query is provided. Only show public repositories for this user.
        # or repos that are shared to the logged in user.
        if user is not None:
            # Filter for all objects by this user
            all_repos = object_list.filter( Q(user__username=user) | Q(org__name=user) )

            # Check permissions against the currently logged in user.
            filtered = []
            for repo in all_repos:
                if repo.is_public or repo.is_form_public or logged_in_user.has_perm( 'view_repository', repo ):
                    filtered.append( repo )

            return filtered

        return False

    def read_detail( self, object_detail, bundle ):

        if bundle.obj.is_public or bundle.obj.is_form_public:
            return True

        logged_in_user = bundle.request.user

        return logged_in_user.has_perm( 'view_repository', bundle.obj )

    def create_detail( self, object_detail, bundle ):
        return True
