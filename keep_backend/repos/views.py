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

from guardian.shortcuts import get_perms, assign_perm, get_users_with_perms, remove_perm, get_groups_with_perms

from api.tasks import insert_csv_data
from backend.db import db, DataSerializer, user_or_organization

from studies.models import StudySerializer
from visualizations.models import VisualizationSerializer
from visualizations.models import FilterSet
from api.filters import FilterSetResource
#from privacy import privatize_geo

from .forms import NewRepoForm, NewBatchRepoForm
from .models import Repository, RepoSerializer

from twofactor.models import UserAPIToken

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
        username = request.GET.get( 'username', None )
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

    # If the repo is part of a study, grab the tracker repo
    tracker_repo = repo.registry()

    if request.method == 'POST':

        if request.POST.get('detail_data_id'):

            repo.update_data( request.POST, request.FILES )


            # ISN Phase 2 hack to redirect back to patient list with necessary
            # querystring parameters.
            #
            ###### BEGIN HACK ######
            if 'provider_id' in request.POST:
                patient = db.data.find( {"label": repo_name, "_id":ObjectId(request.POST['detail_data_id'])} )[0]['data']
                [doc, pat, cluster] = [ patient['provider_id'], patient['patient_id'], patient['cluster_id'] ]
                token = request.POST['key']

                patient_list_url = "/{0}/patient_list/".format(account.username)
                patient_list_url += "?key={0}".format(token)
                patient_list_url += "&provider_id={0}".format(doc)
                patient_list_url += "&cluster_id={0}".format(cluster)
                patient_list_url += "&patient_id={0}".format(pat)

                return HttpResponseRedirect(patient_list_url)
            ####### END HACK #######

            # If part of a study, return to registry
            if tracker_repo:
                destination = { 'repo_name': tracker_repo.name,
                                'username': tracker_repo.owner() }
            else:
                destination = { 'repo_name': repo_name,
                                'username': account.username }

            return HttpResponseRedirect( reverse( 'repo_visualize', kwargs=destination) )
        else:

            # Do validation of the data and add to repo!
            patient_id = repo.add_data( request.POST, request.FILES )

            # ISN Phase 2 hack to redirect back to patient list with necessary
            # querystring parameters.
            #
            ###### BEGIN HACK ######
            if 'provider_id' in request.POST:
                patient = db.data.find( {"label": repo_name, "_id": patient_id} )[0]['data']
                [doc, pat, cluster] = [ patient['provider_id'], patient['patient_id'], patient['cluster_id'] ]
                token = UserAPIToken.objects.filter(user=account)[0]

                patient_list_url = "/{0}/patient_list/".format(account.username)
                patient_list_url += "?key={0}".format(token.key)
                patient_list_url += "&provider_id={0}".format(doc)
                patient_list_url += "&cluster_id={0}".format(cluster)
                patient_list_url += "&patient_id={0}".format(pat)

                return HttpResponseRedirect(patient_list_url)
            ####### END HACK #######

            # Return to organization/user dashboard based on where the "New Repo"
            # button was clicked.  Send Non-users to thank-you page
            if not request.user.is_authenticated():
                return render_to_response( 'finish_survey.html' )

            # If part of a study, return to registry
            elif tracker_repo:
                destination = { 'repo_name': tracker_repo.name,
                                'username': tracker_repo.owner() }

                return HttpResponseRedirect( reverse( 'repo_visualize', kwargs=destination) )

            elif isinstance( account, User ):
                return HttpResponseRedirect(
                            reverse( 'user_dashboard',
                                     kwargs={ 'username': account.username } ) )
            else:
                return HttpResponseRedirect(
                            reverse( 'organization_dashboard',
                                     kwargs={ 'org': account.name } ) )

    serializer = RepoSerializer()
    repo_json = json.dumps( serializer.serialize( [repo] )[0] )
    flat_fields = repo.flatten_fields_with_group()
    first_field = flat_fields[0]

    # Check if first field is question/group with label translations. If the
    # first field is a tracker field, then check the second field for
    # translations. (The tracker field is added automatically and doesn't
    # have translations).
    if 'label' in first_field and first_field['label'] == 'id':
        first_field = flat_fields[1]
    if 'label' in first_field and isinstance(first_field['label'], dict):
        has_translations = True
        translations = first_field['label'].keys
    elif first_field['type'] == 'group' and isinstance( first_field['children'][0]['label'], dict):
        # The first field is a group w/o a translation, so check if the first
        # question in the group has a translation.
        has_translations = True
        translations = first_field['children'][0]['label'].keys
    else:
        has_translations = False
        translations = []

    flat_field_json = json.dumps(flat_fields)

    patient_id = request.GET.get('patient_id', None)

    return render_to_response( 'webform.html',
                               { 'repo': repo,
                                 'registry': tracker_repo,
                                 'repo_json': repo_json,
                                 'flat_fields': flat_fields,
                                 'flat_field_json':flat_field_json,
                                 'has_translations': has_translations,
                                 'translations': translations,
                                 'repo_id': repo.mongo_id,
                                 'account': account,
                                 'patient_id': patient_id
                                  },
                               context_instance=RequestContext( request ))


@require_GET
def repo_viz( request, username, repo_name, filter_param=None ):
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

    # If the repo is part of a study, grab the tracker repo
    tracker_repo = repo.registry()

    # Grab all the permissions!
    permissions = []
    if request.user.is_authenticated():
        permissions = get_perms( request.user, repo )
        for org in request.user.organization_users.all():
            permissions.extend( get_perms( org, repo ) )

    # ISN Phase 2 hacks: allow anyone to view repo
    ######### BEGIN HACK ###########
    # Check to see if the user has access to view this survey
    #if not repo.is_public and 'view_repository' not in permissions:
    #    return HttpResponse( 'Unauthorized', status=401 )
    ######### END HACK ##########

    #----------------------------------------------------------------------
    #
    # Query and serialize data from this repository
    #
    #----------------------------------------------------------------------
    data_query = { 'repo': ObjectId( repo.mongo_id ) }

    if repo.study and filter_param:
        data_query[ 'data.%s' % repo.study.tracker ] = filter_param

    # ISN Phase 2 hacks: filter by provider/cluster
    ######### BEGIN HACK ###########
    if 'provider_id' in request.GET:
        data_query['data.provider_id'] = request.GET['provider_id']
    if 'cluster_id' in request.GET:
        data_query['data.cluster_id'] = request.GET['cluster_id']
    if not 'cluster_id' in request.GET and not 'provider_id' in request.GET:
        data_query['data.nonexistentfield'] = 'returnsemptyquery'

    data = db.data.find( data_query, { 'survey_label': False, 'user': False } )\
                  .sort( [ ('timestamp', pymongo.DESCENDING ) ] )

    if not 'provider_id' in request.GET and not 'cluster_id' in request.GET:
        data = data.limit(50)
    ######### END HACK ##########


    data_serializer = DataSerializer()
    if repo.is_tracker and repo.study:
        linked = Repository.objects.filter( study=repo.study ).exclude( id=repo.id )
        data = data_serializer.dehydrate( data, repo,linked )
    else:
        data = data_serializer.dehydrate( data, repo )

    # Is some unknown user looking at this data?
    # TODO: Make the privatizer take into account
    # geospatial location
    # if 'view_raw' not in permissions:
    #     data = privatize_geo( repo, data )

    # Get all accounts (users and orgs) with permissions to this repo.
    users_with_perms = get_users_with_perms( repo, attach_perms=True )
    # Don't want to show your own account
    users_with_perms.pop( account, None )
    orgs_with_perms = get_groups_with_perms( repo, attach_perms=True )
    account_perms = users_with_perms.copy()
    account_perms.update(orgs_with_perms)

    serializer = RepoSerializer()
    repo_json = json.dumps( serializer.serialize( [repo] )[0] )

    # Grab linked repos if this repo is a "tracker" and part of study
    linked_json = '[]'
    if repo.study and repo.is_tracker:
        # If this repo is a tracker and part of a study, grab all repos that
        # are part of the study so that we can display data links.
        linked = []
        study_repos = Repository.objects.filter( study=repo.study ).exclude( id=repo.id )
        #orgs = request.user.organization_users.all()
        for r in study_repos:
            linked.append(r)
            #if repo.is_public or repo.is_form_public or request.user.has_perm( 'view_repository', repo ):
            #    linked.append(r)
            #else:
            #    for org in orgs:
            #        if 'view_repository' in get_perms(org, r):
            #            linked.append(r)

        linked_json = json.dumps( serializer.serialize( linked ) )

    # Grab the list of visualizations for this repo
    viz_serializer = VisualizationSerializer()
    viz_json = json.dumps( viz_serializer.serialize( repo.visualizations.all() ) )

    # Get JSON for filters using TastyPie serializers
    fsr = FilterSetResource()
    filters = FilterSet.objects.filter(repo=repo.id)
    bundles = [fsr.build_bundle(obj=f, request=request) for f in filters]
    filter_data = [fsr.full_dehydrate(bundle) for bundle in bundles]
    filter_json = fsr.serialize(request, filter_data, 'application/json')
    resource_ids = {'user_id': (request.user.id or -1), 'repo_id': repo.id }

    patient_id = request.GET.get('patient_id')

    return render_to_response( 'visualize.html',
                               { 'repo': repo,
                                 'registry': tracker_repo,

                                 'repo_json': repo_json,
                                 'linked_json': linked_json,
                                 'viz_json': viz_json,
                                 'filter_json': filter_json,
                                 'resource_ids': resource_ids,

                                 'data': json.dumps( data ),

                                 'permissions': permissions,
                                 'account': account,
                                 'account_perms': account_perms,
                                 'patient_id': patient_id,
                                 },
                               context_instance=RequestContext(request) )
