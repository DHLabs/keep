import json
import pymongo

from bson import ObjectId

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from guardian.shortcuts import get_perms, assign_perm, get_users_with_perms, remove_perm

from api.tasks import insert_csv_data
from backend.db import db, dehydrate_survey, user_or_organization

#from privacy import privatize_geo

from .forms import NewRepoForm, NewBatchRepoForm
from .models import Repository, RepoSerializer


@login_required
@require_POST
def insert_data_into_repo( request, repo_id ):
    '''
        Insert data from a CSV into a repo. This is relayed as a task to a
        Celery worker.
    '''

    repo = Repository.objects.get( mongo_id=repo_id )

    # Place the task in the queue
    task = insert_csv_data.delay( file=request.POST.get( 'file_key' ), repo=repo_id )

    # Save the task id so we can go back and check on the task
    repo.add_task( task.task_id, 'csv_insert' )

    return HttpResponseRedirect( reverse( 'repo_visualize',
                                          kwargs={ 'username': request.user.username,
                                                   'repo_name': repo.name } ) )


@login_required
@require_POST
def batch_repo( request ):

    form = NewBatchRepoForm( request.POST, request.FILES, user=request.user )

    if form.is_valid():
        new_repo = form.save()

        return HttpResponseRedirect( reverse( 'repo_visualize',
                                              kwargs={ 'username': request.user.username,
                                                       'repo_name': new_repo.name } ) )


@login_required
@require_POST
def move_repo( request ):

    move_user = User.objects.get( username=request.POST[ 'move_username' ] )
    repository = Repository.objects.get( mongo_id=request.POST[ 'repo' ] )

    repository.move_to( move_user )
    repository.save()

    return HttpResponseRedirect( '/' )


@login_required
def new_repo( request ):
    """
        Creates a new repo under the currently logged in user.
    """
    # Handle XForm upload
    if request.method == 'POST':
        # Check for a valid XForm and parse the file!
        form = NewRepoForm( request.POST, request.FILES, user=request.user )
        print form['name']
        print form['desc']
        print form['privacy']
        print form['survey_json']
        if form.is_valid():
            form.save()
            return HttpResponseRedirect( '/' )
    else:
        form = NewRepoForm()

    user_repos = Repository.objects.filter( user=request.user, org=None )

    repos = []
    for repo in user_repos:
        #I want a flat list of repo fields
        repo_info = {
            'name': repo.name,
            'mongo_id': repo.mongo_id,
            'children': repo.fields() }
        repos.append( repo_info )

    return render_to_response( 'new.html',
                               { 'form': form,
                                 'user_repos': repos },
                               context_instance=RequestContext(request) )


@login_required
def edit_repo( request, repo_id ):
    """
        Edits a data repository
        Takes user to Form Builder
    """
    repo = get_object_or_404( Repository, mongo_id=repo_id )

    # Check that this user has permission to edit this repo
    if not request.user.has_perm( 'delete_repository', repo ):
        return HttpResponse( 'Unauthorized', status=401 )

    if request.method == 'POST':
        form = NewRepoForm( request.POST, request.FILES, user=request.user )
        repo.name = request.POST['name'].replace( ' ','_' )
        repo.description = request.POST['desc']
        repo.save()
        data_repo = db.repo.find_one( ObjectId( repo_id ) )
        newJSON = json.loads( request.POST['survey_json'].strip() )
        newfields = newJSON['children']
        formType = newJSON['type']
        db.repo.update( {"_id":ObjectId( repo_id )},{"$set": {'fields': newfields, 'type': formType}} )
        return HttpResponseRedirect( '/' )
    else:
        form = NewRepoForm()
        form.initial["name"] = repo.name
        form.initial["desc"] = repo.description

    user_repos = Repository.objects.filter( user=request.user, org=None )
    repos = []
    for temp_repo in user_repos:
        #I want a flat list of repo fields
        repo_info = {
            'name': temp_repo.name,
            'mongo_id': temp_repo.mongo_id,
            'children': temp_repo.fields() }
        repos.append( repo_info )

    data_repo = db.repo.find_one( ObjectId( repo_id ) )
    temp_dict = {}
    temp_dict['children'] = data_repo['fields']
    if 'type' in data_repo:
        temp_dict['type'] = data_repo['type']
    else:
        temp_dict['type'] = "survey"

    return render_to_response( 'new.html',
                               {'form': form,
                                'repo_json': json.dumps(temp_dict),
                                'user_repos': repos },
                               context_instance=RequestContext(request) )


@login_required
def delete_repo( request, repo_id ):
    """
        Delete a data repository.

        Checks if the user is the original owner of the repository and removes
        the repository and the accompaning repo data.
    """

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
    """
        Toggle's a data repo's "publicness". Only the person who owns the form
        is allowed to make such changes to the form settings.
    """

    repo = get_object_or_404( Repository, mongo_id=repo_id )

    if not request.user.has_perm( 'share_repository', repo ):
        return HttpResponse( 'Unauthorized', status=401 )

    repo.is_public = not repo.is_public
    repo.save()

    return HttpResponse( json.dumps( { 'success': True,
                                       'public': repo.is_public } ),
                         mimetype='application/json' )


@csrf_exempt
@require_POST
@login_required
def toggle_form_access( request, repo_id ):
    """
        Toggle's a form's access(Whether someone can view the form and submit data).
        Only the person who owns the form
        is allowed to make such changes to the form settings.
    """

    repo = get_object_or_404( Repository, mongo_id=repo_id )

    if not request.user.has_perm( 'share_repository', repo ):
        return HttpResponse( 'Unauthorized', status=401 )

    repo.is_form_public = not repo.is_form_public
    repo.save()

    return HttpResponse( json.dumps( { 'success': True,
                                       'public': repo.is_form_public } ),
                         mimetype='application/json' )

@csrf_exempt
@login_required
def share_repo( request, repo_id ):
    """
        Modifies sharing permissions for specific users
    """

    repo = get_object_or_404( Repository, mongo_id=repo_id )

    if not request.user.has_perm( 'share_repository', repo ):
        return HttpResponse( 'Unauthorized', status=401 )

    if request.method == 'POST':
        username = request.POST.get( 'username', None )
    elif request.method == 'DELETE':
        username = json.loads( request.body ).get( 'username', None )
    else:
        username = request.GET.get( 'username', None )

    # Grab the user/organization based on the username
    account = user_or_organization( username )
    if account is None:
        return HttpResponse( status=404 )

    if account == request.user:
        return HttpResponse( status=401 )

    # Remove permissions from user
    if request.method == 'DELETE':
        old_permissions = get_perms( account, repo )
        for old_permission in old_permissions:
            remove_perm( old_permission, account, repo )
        return HttpResponse( 'success', status=204 )
    # Add certain permissions for a specific user
    else:
        new_permissions = request.POST.get( 'permissions', '' ).split(',')
        for new_permission in new_permissions:
            assign_perm( new_permission, account, repo )
        return HttpResponse( 'success', status=200 )


@csrf_exempt
def webform( request, username, repo_name ):
    """
        Simply grab the survey data and send it on the webform. The webform
        will handle rendering and submission of the final data to the server.
    """

    account = user_or_organization( username )
    if account is None:
        return HttpResponse( status=404 )

    # Grab the repository
    repo = Repository.objects.get_by_username( repo_name, username )
    if repo is None:
        return HttpResponse( status=404 )

    if request.method == 'POST':

        # Do validation of the data and add to repo!
        repo.add_data( request.POST, request.FILES )

        # Return to organization/user dashboard based on where the "New Repo"
        # button was clicked.  Send Non-users to thank-you page
        if not request.user.is_authenticated():
            return render_to_response( 'finish_survey.html' )

        elif isinstance( account, User ):
            return HttpResponseRedirect(
                        reverse( 'user_dashboard',
                                 kwargs={ 'username': account.username } ) )
        else:
            return HttpResponseRedirect(
                        reverse( 'organization_dashboard',
                                 kwargs={ 'org': account.name } ) )

    return render_to_response( 'webform.html',
                               { 'repo': repo,
                                 'repo_id': repo.mongo_id,
                                 'account': account },
                               context_instance=RequestContext( request ))


@require_GET
def repo_viz( request, username, repo_name ):
    """
        View repo <repo_name> under user <username>.

        Does the checks necessary to determine whether the current user has the
        authority to view the current repository.
    """

    # Grab the user/organization based on the username
    account = user_or_organization( username )
    if account is None:
        return HttpResponse( status=404 )

    # Grab the repository
    repo = Repository.objects.get_by_username( repo_name, username )
    if repo is None:
        return HttpResponse( status=404 )

    # Grab all the permissions!
    permissions = []
    if request.user.is_authenticated():
        permissions = get_perms( request.user, repo )
        for org in request.user.organization_users.all():
            permissions.extend( get_perms( org, repo ) )

    # Check to see if the user has access to view this survey
    if not repo.is_public and 'view_repository' not in permissions:
        return HttpResponse( 'Unauthorized', status=401 )

    # Grab the data for this repository
    data = db.data.find( { 'repo': ObjectId( repo.mongo_id ) },
                         { 'survey_label': False,
                           'user': False } )\
                  .sort( [ ('timestamp', pymongo.DESCENDING ) ] )\
                  .limit( 50 )

    data = dehydrate_survey( data )

    # Is some unknown user looking at this data?
    # TODO: Make the privatizer take into account
    # geospatial location
    # if 'view_raw' not in permissions:
    #     data = privatize_geo( repo, data )

    usePerms = get_users_with_perms( repo, attach_perms=True )
    usePerms.pop( account, None )

    serializer = RepoSerializer()
    repo_json = json.dumps( serializer.serialize( [repo] )[0] )

    return render_to_response( 'visualize.html',
                               { 'repo': repo,
                                 'repo_json': repo_json,
                                 'data': json.dumps( data ),
                                 'permissions': permissions,
                                 'account': account,
                                 'users_perms': usePerms },
                               context_instance=RequestContext(request) )
