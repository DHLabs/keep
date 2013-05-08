import json

from bson import ObjectId

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.http import require_POST, require_GET

from backend.db import db
from repos.forms import NewRepoForm

from .forms import NewOrganizationForm
from .models import Organization, OrganizationUser


@login_required
def organization_new( request ):

    user = request.user

    if request.method == 'POST':
        form = NewOrganizationForm( request.POST )

        if form.is_valid():
            new_org = Organization( name=form.cleaned_data[ 'name' ],
                                    gravatar=form.cleaned_data[ 'gravatar' ],
                                    owner=user )
            new_org.save()

            new_org_user = OrganizationUser( user=user,
                                             organization=new_org )
            new_org_user.is_admin = True
            new_org_user.save()

            return HttpResponseRedirect(
                        reverse( 'user_dashboard',
                                 kwargs={ 'username': user.username } ) )
    else:
        form = NewOrganizationForm()

    return render_to_response( 'organization_new.html', { 'form': form },
                               context_instance=RequestContext(request) )


@login_required
def organization_delete( request, org ):

    user = request.user
    org  = get_object_or_404( Organization, name=org )

    if Organization.has_user( org, user ):

        # Delete any repos associated with this organization
        repos = db.survey.find( { 'org': org.id } )
        repos = [ repo[ '_id' ] for repo in repos ]

        db.survey.remove( { '_id': { '$in': repos } } )
        db.data.remove( { 'repo': { '$in': repos } } )

        # Delete all the org user objects under this org
        org_users = OrganizationUser.objects.filter( organization=org )
        for org_user in org_users:
            org_user.delete()

        # Delete the main org object
        org.delete()

    return HttpResponseRedirect(
                reverse( 'user_dashboard',
                         kwargs={ 'username': user.username } ) )


@login_required
def organization_dashboard( request, org ):

    account = get_object_or_404( Organization, name=org )
    is_owner = request.user == account.owner

    repos = db.survey.find( { 'org': account.id } )
    repos = [ repo for repo in repos ]
    for repo in repos:
        # Replace _id with mongo_id since the templates don't place nicely with
        # variables that have an underscore in front.
        repo[ 'id' ] = repo[ '_id' ]

        # Count the number of submissions for this repo
        repo[ 'submission_count' ] = db.data\
                                       .find( {'repo':
                                              ObjectId(repo[ '_id' ])})\
                                       .count()
        del repo[ '_id' ]

    members = OrganizationUser.objects.filter( organization=account )

    return render_to_response( 'organization_dashboard.html',
                               { 'account': account,
                                 'members': members,
                                 'is_owner': is_owner,
                                 'repos': repos },
                               context_instance=RequestContext(request) )


@login_required
def organization_repo_new( request, org ):
    '''
        Create a new data repository under <org>.
    '''

    org = get_object_or_404( Organization, name=org )

    if request.method == 'POST':

        form = NewRepoForm( request.POST, request.FILES, org=org )

        # Check for a valid XForm and parse the file!
        if form.is_valid():

            repo = form.save()
            db.survey.insert( repo )

            return HttpResponseRedirect( reverse( 'organization_dashboard',
                                                  kwargs={ 'org': org.name } ))

    else:
        form = NewRepoForm()

    return render_to_response( 'new.html', { 'form': form },
                               context_instance=RequestContext(request) )


@login_required
@require_POST
def organization_member_add( request, org, user ):
    '''
        Request a user become a member of an organization.
    '''

    org  = get_object_or_404( Organization, name=org )
    user = get_object_or_404( User, username=user )

    org_user = get_object_or_404( OrganizationUser,
                                  user=request.user,
                                  organization=org )

    # Check that the current user is the owner of the org or is an admin
    response = { 'success': False }

    # Don't add users who are already members
    res = OrganizationUser.objects.filter( organization=org,
                                           user=user )
    if len( res ) == 0:
        if org.owner == user or org_user.is_admin:
            org.add_user( user )
            response[ 'success' ] = True

    return HttpResponse( json.dumps( response ),
                         content_type='application/json' )


@login_required
@require_GET
def organization_member_accept( request, org, user ):
    '''
        Request a user become a member of an organization.
    '''
    org  = get_object_or_404( Organization, name=org )
    user = get_object_or_404( User, username=user )

    # Is the user this acceptance is for the current user?
    if request.user != user:
        return HttpResponse( status=404 )

    # Great grab this user and toggle the pending variable
    org_user = get_object_or_404( OrganizationUser,
                                  user=user,
                                  organization=org )
    org_user.pending = False
    org_user.save()

    return HttpResponseRedirect(
            reverse( 'user_dashboard',
                     kwargs={ 'username': user.username } ) )


@login_required
@require_GET
def organization_member_ignore( request, org, user ):
    '''
        Request a user become a member of an organization.
    '''
    org  = get_object_or_404( Organization, name=org )
    user = get_object_or_404( User, username=user )

    # Is the user this acceptance is for the current user?
    if request.user != user:
        return HttpResponse( status=404 )

    # Great grab this user and toggle the pending variable
    org_user = get_object_or_404( OrganizationUser,
                                  user=user,
                                  organization=org )
    org_user.delete()

    return HttpResponseRedirect(
            reverse( 'user_dashboard',
                     kwargs={ 'username': user.username } ) )
