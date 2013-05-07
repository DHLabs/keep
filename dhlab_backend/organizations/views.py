from bson import ObjectId

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

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
            new_org_user.save()

            return HttpResponseRedirect(
                        reverse( 'user_dashboard',
                                 kwargs={ 'username': user.username } ) )
    else:
        form = NewOrganizationForm()

    return render_to_response( 'organization_new.html', { 'form': form },
                               context_instance=RequestContext(request) )


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
