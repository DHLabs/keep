from backend.db import db
from backend.forms import RegistrationFormUserProfile
from backend.forms import ResendActivationForm
from backend.forms import ReportForm

import json
from bson import json_util, ObjectId

from django.core.urlresolvers import reverse
from django.contrib.sites.models import RequestSite
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from organizations.models import Organization
from registration.models import RegistrationProfile
from repos.models import Repository
from twofactor.models import UserAPIToken


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
    organizations = Organization.objects.filter( users=user )

    patients = Repository.objects.filter( user=user, name='patients' )
    patient_list = []
    if len( patients ) > 0:
        patients = patients[0]
        patient_list = []
        patients = db.data.find( { 'repo': ObjectId( patients.mongo_id ) } )

        for patient in patients:
            patient_list.append( patient[ 'data' ] )

    # Grab a list of forms uploaded by the user
    if is_other_user:
        user_repos = Repository.objects.filter( user=user, org=None, is_public=True )
        shared_repos = Repository.objects.filter( org__in=organizations,
                                                  is_public=True )
    else:
        user_repos = Repository.objects.filter( user=user, org=None )
        shared_repos = Repository.objects.filter( org__in=organizations )

    return render_to_response( 'dashboard.html',
                               {'patients': patient_list,
                                'user_repos': user_repos,
                                'shared_repos': shared_repos,
                                'is_other_user': is_other_user,
                                'account': user,
                                'organizations': organizations },
                               context_instance=RequestContext(request) )


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

@login_required
def build_report( request ):

    if request.method == 'POST':
        form = ReportForm( request.POST, request.FILES )

        if( form.is_valid ):
            #build form
            data = request.POST[ 'report_json' ].strip()

            #TODO: refactor report building to separate file, will get quite big eventually

            if len( data ) == 0:
                return None

            # Attempt to load the into a dict
            try:
                data = json.loads( data )
            except Exception:
                return None

            report_items = []

            print data

            for item in data:
                report_item = {}
                report_item['form_name'] = item['form_name']
                report_item['form_question'] = item['form_question']

                query = { 'repo': ObjectId( item['form_id'] ) }
                #todo: add timestamp filtering

                results = db.data.find( query )
                sum = 0
                num_responses = 0

                for result in results:
                    question_data = result['data'][ item['form_question'] ]
                    print question_data
                    if item['report_type'] == 'incidence':
                        if question_data:
                            num_responses = num_responses + 1
                    else:
                        if is_number(question_data):
                            sum = sum + int(question_data)
                            num_responses = num_responses + 1

                if item['report_type'] == 'incidence':
                    report_string = "%d" % num_responses + ' occurences'
                else:
                    if num_responses > 0:
                        average = (float(sum) / float(num_responses))
                    else:
                        average = 0
                    report_string = "%.2f" % average
                    report_string += " average from " + "%d" % num_responses + " responses out of " + "%d" % results.count() + " surveys"

                report_item['report_string'] = report_string

                report_items.append( report_item )

            print report_items

            return render_to_response( 'report.html',
                                      {'report_items': report_items },
                                      context_instance=RequestContext(request) )
    else:
        form = ReportForm()

    user_repos = Repository.objects.filter( user=request.user, org=None )

    repos = []
    for repo in user_repos:
        repo_info = {
            'name': repo.name,
            'mongo_id': repo.mongo_id,
            'children': repo.fields() }
        repos.append( repo_info )

    return render_to_response( 'report_builder.html',
                                { 'user_repos': json.dumps( repos ),
                                  'form': form },
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

    return render_to_response( 'settings.html',
                               {'api_tokens': api_tokens},
                               context_instance=RequestContext(request))
