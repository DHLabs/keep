import json

from backend.forms import RegistrationFormUserProfile
from backend.forms import ResendActivationForm

from django.core import serializers
from django.core.urlresolvers import reverse
from django.contrib.sites.models import RequestSite
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from organizations.models import OrganizationUser
from registration.models import RegistrationProfile
from repos.models import Repository, RepoSerializer
from studies.models import Study, StudySerializer
from twofactor.models import UserAPIToken, UserAuthToken


def home( request ):
    if request.user.is_authenticated():
        return HttpResponseRedirect(
                    reverse( 'user_dashboard',
                             kwargs={ 'username': request.user.username } ) )

    return render_to_response( 'index.html' )


def register( request ):
    if request.method == 'POST':
        form = RegistrationFormUserProfile( request.POST )
        if form.is_valid():
            ( new_user, user_token ) = form.save()

            # Send activation email
            for profile in RegistrationProfile.objects.filter(user=new_user):
                profile.send_activation_email( RequestSite( request ) )

            return render_to_response('registration/reg_complete.html',
                                      {'user_token': user_token.google_url(),
                                       'email': new_user.email } )
    else:
        form = RegistrationFormUserProfile()

    return render_to_response( 'registration/registration_form.html',
                               {'form': form },
                               context_instance=RequestContext(request) )


def registration_complete( request ):
    return render_to_response( 'registration/activate.html' )


def resend_activation( request ):

    status = None

    if request.method == 'POST':

        form = ResendActivationForm( request.POST )

        if form.is_valid():
            email = form.cleaned_data[ 'email' ]
            users = User.objects.filter( email=email, is_active=0 )

            site = RequestSite( request )

            if users.count() == 0:
                form._errors[ 'email' ] = '''Account for email address is not
                                             recognized'''
            else:
                user = users[0]
                for profile in RegistrationProfile.objects.filter(user=user):
                    if not profile.activation_key_expired():
                        profile.send_activation_email( site )

                status = 'Email Activation Sent!'
    else:
        form = ResendActivationForm()

    return render_to_response( 'registration/resend_activation.html',
                               { 'form': form,
                                 'status': status },
                               context_instance=RequestContext( request ) )


@login_required
def user_dashboard( request, username ):
    '''
        Dashboard seen when a user signs in or views another user's profile.

        The dashboard contains links to a users the private/public data repos.
        Private repos are only shown if the user has permission to view them.
    '''
    # Are we looking at our own profile or someone elses?
    is_other_user = request.user.username != username

    user = get_object_or_404( User, username=username )

    # Find all the organization this user belongs to
    organizations = OrganizationUser.objects.filter( user=user )

    # Grab a list of forms uploaded by the user
    if is_other_user:
        user_repos = Repository.objects.list_by_user( user=user,
                                                      organizations=organizations,
                                                      public=True )
        user_studies = []
    else:
        user_repos = Repository.objects.list_by_user( user=user,
                                                      organizations=organizations )
        user_studies = Study.objects.filter( user=user )


    serializer = RepoSerializer()
    repo_json = json.dumps( serializer.serialize( user_repos ) )

    serializer = StudySerializer()
    study_json = json.dumps( serializer.serialize( user_studies ) )

    return render_to_response( 'dashboard.html',
                               { 'user_studies': study_json,
                                 'user_repos': repo_json,
                                 'is_other_user': is_other_user,
                                 'account': user,
                                 'organizations': organizations },
                               context_instance=RequestContext(request) )


@login_required
def generate_api_key( request ):
    UserAPIToken.objects.create( user=request.user,
                                 name=request.GET.get( 'name', '' ) )
    return HttpResponseRedirect( '/settings' )


@login_required
def delete_api_key( request, key ):
    token = UserAPIToken.objects.get(id=key)
    token.delete()
    return HttpResponseRedirect( '/settings' )


@login_required
def settings( request ):

    api_tokens = UserAPIToken.objects.filter(user=request.user)
    auth_token = UserAuthToken.objects.get( user=request.user )

    return render_to_response( 'settings.html',
                               {'api_tokens': api_tokens,
                                'auth_token': auth_token },
                               context_instance=RequestContext(request))
