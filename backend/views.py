from bson import ObjectId

from backend.db import db
from backend.forms import RegistrationFormUserProfile, UploadXForm

from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt

from twofactor.models import UserAPIToken

from pyxform.xls2json import SurveyReader


def webform( request, form_id ):
    '''
        Simply grab the survey data and send it on the webform. The webform
        will handle rendering and submission of the final data to the server.
    '''
    data = db.survey.find_one( { '_id': ObjectId( form_id ) } )
    return render_to_response( 'forms/get.html',
                                { 'form': data,
                                  # Convert the form id to a string for easy
                                  # access
                                  'form_id': str( data[ '_id' ] ) } )

'''
@csrf_exempt
def submission2( request ):

    if request.method == 'POST':
        data = simplejson.dumps( { 'success': True } )
        return HttpResponse( data, mimetype='application/json' )

    return HttpResponseNotAllowed( ['POST'] )
'''

def submission( request,username ):

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
        return HttpResponseRedirect( '/dashboard' )
    else:
        return HttpResponseRedirect( '/accounts/login' )


def register( request ):
    if request.method == 'POST':
        form = RegistrationFormUserProfile( request.POST )
        if form.is_valid():
            ( new_user, user_token ) = form.save()

            return render_to_response('registration/reg_complete.html',
                                      {'user_token': user_token.google_url()})
    else:
        form = RegistrationFormUserProfile()

    return render_to_response( 'registration/registration_form.html',
                                {'form': form },
                                context_instance=RequestContext(request) )


@login_required
def dashboard( request ):
    # Handle XForm upload
    if request.method == 'POST':

        form = UploadXForm( request.POST, request.FILES )

        # Check for a valid XForm and parse the file!
        if form.is_valid():

            # Parse the file and store into our database
            try:
                survey = SurveyReader( request.FILES[ 'file' ] )

                if len( survey._warnings ) > 0:
                    print 'Warnings parsing xls file!'

                data = survey.to_json_dict()
                # Store who uploaded this form
                data[ 'user' ]      = request.user.id
                # Store when this form was uploaded
                data[ 'uploaded' ]  = datetime.now()

                db.survey.insert( data )

            except Exception as e:
                print e
    else:
        form = UploadXForm()

    # Grab a list of forms uploaded by the user
    user_forms = db.survey.find( { 'user': request.user.id } )

    # TODO: Find better way of converting _id to mongo_id
    user_forms = [ xform for xform in user_forms ]
    for xform in user_forms:
        xform[ 'mongo_id' ] = xform[ '_id' ]

    return render_to_response(
                'dashboard.html',
                { 'form': form, 'user_forms': user_forms },
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

    return render_to_response(
                'settings.html',
                {'api_tokens': api_tokens},
                context_instance=RequestContext(request))
