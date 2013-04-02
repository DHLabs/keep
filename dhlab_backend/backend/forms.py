import re

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from registration.forms import RegistrationFormUniqueEmail
from registration.models import RegistrationProfile

from twofactor.models import UserAuthToken


class UploadXForm( forms.Form ):
    file  = forms.FileField(label='XForm File')


class ResendActivationForm( forms.Form ):
    email = forms.EmailField(widget=forms.TextInput())


class RegistrationFormUserProfile( RegistrationFormUniqueEmail ):
    class Meta:
        pass

    _reserved_usernames = [
        'accounts', 'about', 'admin', 'clients', 'crowdform', 'crowdforms',
        'data', 'forms', 'maps', 'odk', 'people', 'submit', 'submission',
        'support', 'syntax', 'xls2xform', 'users', 'worldbank', 'unicef',
        'who', 'wb', 'wfp', 'save', 'ei', 'modilabs', 'mvp', 'unido',
        'unesco', 'savethechildren', 'worldvision', 'afsis']

    username = forms.CharField(widget=forms.TextInput(), max_length=30)
    email    = forms.EmailField(widget=forms.TextInput())

    legal_usernames_re = re.compile("^\w+$")

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        if username in self._reserved_usernames:
            raise forms.ValidationError(
                _(u'%s is a reserved name, please choose another') % username)
        elif not self.legal_usernames_re.search(username):
            raise forms.ValidationError(
                _(u'username may only contain alpha-numeric characters and '
                  u'underscores'))
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_(u'%s already exists') % username)

    def save(self, profile_callback=None):
        new_user = RegistrationProfile.objects.create_inactive_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email'],
            site='http://distributedhealth.org',
            send_email=False)

        new_user.is_active = True
        #RegistrationProfile.objects.activate_user( new_user.activation_key )

        auth_token = UserAuthToken(user=new_user)
        auth_token.save()

        print 'Password: ', new_user.password

        return ( new_user, auth_token )
