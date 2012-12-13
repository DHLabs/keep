from backend.forms import RegistrationFormUserProfile, UploadXForm

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from pyxform.xls2json_backends import xls_to_dict


@login_required
def dashboard( request ):
    if request.method == 'POST':
        form = UploadXForm( request.POST, request.FILES )
        if form.is_valid():
            # Parse the file
            try:
                print xls_to_dict( request.FILES[ 'file' ] )
            except Exception as e:
                print e
    else:
        form = UploadXForm()

    return render_to_response(
                'dashboard.html',
                { 'form': form },
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
