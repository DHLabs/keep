from bson import ObjectId

from backend.db import db, encrypt_survey

from backend.forms import RegistrationFormUserProfile
from backend.forms import ResendActivationForm

from datetime import datetime

from django.contrib.sites.models import RequestSite
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson

from registration.models import RegistrationProfile

from twofactor.models import UserAPIToken


def submission( request, username ):

    if request.method == 'POST':
        user = User.objects.get(username=username)
        survey_data = {
            # User ID of the person who uploaded the form (not the data)
            'user':         user.id,
            # Survey/form ID associated with this data
            'survey':       survey[ '_id' ],
            # Timestamp of when this submission was received
            'timestamp':    datetime.utcnow(),
            # The validated & formatted survey data.
            'data':         encrypt_survey( valid_data )
        }
        db.survey_data.insert(survey_data)

        data = simplejson.dumps( { 'success': True } )
        return HttpResponse( data, mimetype='application/json' )

    return HttpResponseNotAllowed( ['POST'] )


def home( request ):
    if request.user.username:
        return HttpResponseRedirect( '/%s' % ( request.user.username ) )
    else:
        return HttpResponseRedirect( '/accounts/login' )


def register( request ):
    if request.method == 'POST':
        form = RegistrationFormUserProfile( request.POST )
        if form.is_valid():
            ( new_user, user_token ) = form.save()

            # Send activation email
            for profile in RegistrationProfile.objects.filter(user=new_user):
                profile.send_activation_email( RequestSite( request ) )

            return render_to_response('registration/reg_complete.html',
                                      {'user_token': user_token.google_url()})
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
    user = get_object_or_404( User, username=username )

    # Grab a list of forms uploaded by the user
    user_forms = db.survey.find( { 'user': user.id } )

    # TODO: Find better way of converting _id to mongo_id
    user_forms = [ xform for xform in user_forms ]
    for xform in user_forms:
        # Replace _id with mongo_id since the templates don't place nicely with
        # variables that have an underscore in front.
        xform[ 'mongo_id' ] = xform[ '_id' ]
        del xform[ '_id' ]

        xform[ 'submission_count' ] = db.survey_data\
                                        .find( {'survey':
                                               ObjectId(xform[ 'mongo_id' ])})\
                                        .count()

    return render_to_response( 'dashboard.html',
                               { 'user_forms': user_forms,
                                 'account': user },
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
