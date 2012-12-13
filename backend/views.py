from backend.db import db
from backend.forms import RegistrationFormUserProfile, UploadXForm

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from pyxform.xls2json import SurveyReader


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
                data[ 'user' ] = request.user.id

                db.survey.insert( data )

            except Exception as e:
                print e
    else:
        form = UploadXForm()

    # Grab a list of forms uploaded by the user
    user_forms = db.survey.find( { 'user': request.user.id } )
    user_forms = [ xform for xform in user_forms ]

    return render_to_response(
                'dashboard.html',
                { 'form': form, 'user_forms': user_forms },
                context_instance=RequestContext(request) )


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
