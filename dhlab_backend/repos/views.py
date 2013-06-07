import json

from bson import ObjectId

from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from guardian.shortcuts import get_perms

from backend.db import db, dehydrate_survey, user_or_organization

#from privacy import privatize_geo

from . import validate_and_format
from .forms import NewRepoForm
from .models import Repository


@login_required
def new_repo( request ):
    '''
        Creates a new user under the currently logged in user.
    '''
    # Handle XForm upload
    if request.method == 'POST':
        # Check for a valid XForm and parse the file!
        form = NewRepoForm( request.POST, request.FILES, user=request.user )
        if form.is_valid():
            form.save()
            return HttpResponseRedirect( '/' )
    else:
        form = NewRepoForm()

    return render_to_response( 'new.html', { 'form': form },
                               context_instance=RequestContext(request) )


@login_required
def delete_repo( request, repo_id ):
    '''
        Delete a data repository.

        Checks if the user is the original owner of the repository and removes
        the repository and the accompaning repo data.
    '''

    repo = get_object_or_404( Repository, mongo_id=repo_id )

    # Check that this user has permission to delete this repo
    if not request.user.has_perm( 'delete_repository', repo ):
        return HttpResponse( 'Unauthorized', status=401 )

    # Delete the sucker
    repo.delete()

    return HttpResponseRedirect( '/' )


@csrf_exempt
@require_POST
@login_required
def toggle_public( request, repo_id ):
    '''
        Toggle's a data repo's "publicness". Only the person who owns the form
        is allowed to make such changes to the form settings.
    '''

    repo = get_object_or_404( Repository, mongo_id=repo_id )

    if not request.user.has_perm( 'share_repository', repo ):
        return HttpResponse( 'Unauthorized', status=401 )

    repo.is_public = not repo.is_public
    repo.save()

    return HttpResponse( json.dumps( { 'success': True,
                                       'public': repo.is_public } ),
                         mimetype='application/json' )


@csrf_exempt
def webform( request, username, repo_name ):
    '''
        Simply grab the survey data and send it on the webform. The webform
        will handle rendering and submission of the final data to the server.
    '''

    account = user_or_organization( username )
    if account is None:
        return HttpResponse( status=404 )

    repo = Repository.get_repo( name=repo_name, account=account )
    if repo is None:
        return HttpResponse( status=404 )

    if request.method == 'POST':

        # Do basic validation of the data
        valid_data = validate_and_format( repo, request.POST )
        Repository.add_data( repo=repo,
                             data=valid_data,
                             account=account )

        # Return to organization/user dashboard based on where the "New Repo"
        # button was clicked.
        if isinstance( account, User ):
            return HttpResponseRedirect(
                        reverse( 'user_dashboard',
                                 kwargs={ 'username': account.username } ) )
        else:
            return HttpResponseRedirect(
                        reverse( 'organization_dashboard',
                                 kwargs={ 'org': account.name } ) )

    return render_to_response( 'get.html',
                               { 'repo': repo,
                                 'repo_id': str( repo[ '_id' ] ),
                                 'account': account },
                               context_instance=RequestContext( request ))


@require_GET
def repo_viz( request, username, repo_name ):
    '''
        View repo <repo_name> under user <username>.

        Does the checks necessary to determine whether the current user has the
        authority to view the current repository.
    '''

    # Grab the user/organization based on the username
    account = user_or_organization( username )
    if account is None:
        return HttpResponse( status=404 )

    # Grab the repository
    repo = Repository.objects.get( Q(name=repo_name), Q(user__username=username) | Q(org__name=username) )
    if repo is None:
        return HttpResponse( status=404 )

    permissions = get_perms( request.user, repo )

    # Check to see if the user has access to view this survey
    if not repo.is_public and 'view_repository' not in permissions:
        return HttpResponse( 'Unauthorized', status=401 )

    # Grab the data for this repository
    data = db.data.find( {'repo': ObjectId( repo.mongo_id )} )
    data = dehydrate_survey( data )

    # Is some unknown user looking at this data?
    # TODO: Make the privatizer take into account
    # geospatial location
    # if 'view_raw' not in permissions:
    #     data = privatize_geo( repo, data )

    if isinstance( account, User ):
        account_name = account.username
    else:
        account_name = account.name

    return render_to_response( 'visualize.html',
                               { 'repo': repo,
                                 'sid': repo.mongo_id,
                                 'data': json.dumps( data ),
                                 'permissions': permissions,
                                 'account': account,
                                 'account_name': account_name },
                               context_instance=RequestContext(request) )
