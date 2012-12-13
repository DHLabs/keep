from backend.forms import RegistrationFormUserProfile

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext


@login_required
def dashboard( request ):
    return render_to_response( 'dashboard.html' )


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
