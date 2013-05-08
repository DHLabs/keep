import json

from bson import ObjectId
from datetime import datetime

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from backend.db import db, dehydrate_survey, user_or_organization
from backend.db import Repository

from organizations.models import Organization
from privacy import privatize_geo

from . import validate_and_format
from .forms import NewRepoForm, BuildRepoForm


@login_required
def new_repo( request ):
    '''
        Creates a new user under the currently logged in user.
    '''
    # Handle XForm upload
    if request.method == 'POST':

        form = NewRepoForm( request.POST, request.FILES, user=request.user )

        # Check for a valid XForm and parse the file!
        if form.is_valid():

            repo = form.save()
            db.survey.insert( repo )

            return HttpResponseRedirect( '/' )
    else:
        form = NewRepoForm()

    return render_to_response( 'new.html', { 'form': form },
                               context_instance=RequestContext(request) )


@login_required
def build_form( request ):
    '''
        Builds form.
        '''
    # Handle XForm upload
    if request.method == 'POST':

        form = BuildRepoForm( request.POST )

        # Check for a valid XForm and parse the file!
        if form.is_valid():

            # Check that this form name isn't already taken by the user
            form_exists = db.survey.find( { 'name': form.cleaned_data['name'],
                                            'user': request.user.id } )

            if form_exists.count() != 0:
                errors = form._errors.setdefault( 'name', ErrorList() )
                errors.append( 'Repository already exists with this name' )
            else:

                data = json.loads(request.POST['surveyjson'])

                # Basic form name/description
                data[ 'name' ] = form.cleaned_data[ 'name' ]
                data[ 'description' ] = form.cleaned_data[ 'desc' ]

                # Needed for xform formatting
                data[ 'title' ]       = form.cleaned_data[ 'name' ]
                data[ 'id_string' ]   = form.cleaned_data[ 'name' ]

                # Is this form public?
                data[ 'public' ] = form.cleaned_data[ 'privacy' ] == 'public'

                # Store who uploaded this form
                data[ 'user' ]      = request.user.id

                data[ 'type' ]      = 'survey'

                # Store when this form was uploaded
                data[ 'uploaded' ]  = datetime.now()

                print data

                db.survey.insert( data )

                return HttpResponseRedirect( '/' )
        else:
            print "form is not valid"

    else:
        form = BuildRepoForm()

    return render_to_response( 'build_form.html', { 'form': form },
                               context_instance=RequestContext(request) )


@login_required
def delete_repo( request, repo_id ):
    '''
        Delete a data repository.

        Checks if the user is the original owner of the repository and removes
        the repository and the accompaning repo data.
    '''

    survey = db.survey.find_one( { '_id': ObjectId( repo_id ) },
                                 { 'user': True } )

    if survey[ 'user' ] != request.user.id:
        return HttpResponse( 'Unauthorized', status=401 )

    db.survey.remove( { '_id': ObjectId( repo_id ) } )
    db.data.remove( { 'repo': ObjectId( repo_id ) } )

    return HttpResponseRedirect( '/' )


@csrf_exempt
@require_POST
@login_required
def toggle_public( request, repo_id ):
    '''
        Toggle's a data repo's "publicness". Only the person who owns the form
        is allowed to make such changes to the form settings.
    '''

    # Find a survey, only looking for the user field
    survey = db.survey.find_one( { '_id': ObjectId( repo_id ) },
                                 { 'user': True, 'public': True } )

    # Check if the owner of the survey matches the user who is logged in
    if survey[ 'user' ] != request.user.id:
        return HttpResponse( 'Unauthorized', status=401 )

    if 'public' in survey:
        survey[ 'public' ] = not survey[ 'public' ]
    else:
        survey[ 'public' ] = True

    db.survey.update( { '_id': ObjectId( repo_id ) },
                      { '$set': { 'public': survey[ 'public' ] } } )

    return HttpResponse( json.dumps( { 'success': True,
                                       'public': survey[ 'public' ] } ),
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
    repo = Repository.get_repo( repo_name, account )
    if repo is None:
        return HttpResponse( status=404 )

    # Grab the user's permissions for this repository
    permissions = Repository.permissions( repo=repo,
                                          account=account,
                                          current_user=request.user )

    # Check to see if the user has access to view this survey
    if 'view' not in permissions:
        return HttpResponse( 'Unauthorized', status=401 )

    # Grab the data for this repository
    data = db.data.find( {'repo': ObjectId( repo[ '_id' ] )} )
    data = dehydrate_survey( data )

    # Is some unknown user looking at this data?
    if 'view_raw' not in permissions:
        data = privatize_geo( repo, data )

    if isinstance( account, User ):
        account_name = account.username
    else:
        account_name = account.name

    return render_to_response( 'visualize.html',
                               { 'repo': repo,
                                 'sid': repo[ '_id' ],
                                 'data': json.dumps( data ),
                                 'permissions': permissions,
                                 'account': account,
                                 'account_name': account_name },
                               context_instance=RequestContext(request) )


@require_GET
def map_visualize( request ):
    return render_to_response( 'map_visualize.html',
                               context_instance=RequestContext(request) )
