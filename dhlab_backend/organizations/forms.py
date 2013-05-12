import re

from django import forms
from django.contrib.auth.models import User

from .models import Organization


class NewOrganizationForm( forms.Form ):

    name    = forms.CharField()

    gravatar = forms.EmailField( required=False )
    desc     = forms.CharField( widget=forms.Textarea, required=False )

    _reserved_names = [ 'new', 'manage', 'delete', 'accounts', 'about',
                        'admin', 'clients', 'data', 'forms', 'maps',
                        'people', 'submit', 'submission', 'support', 'users' ]

    def clean_name( self ):
        '''
            Ensure that there are no organizations/users with this same name
            already!
        '''
        data = self.cleaned_data[ 'name' ].strip()

        if re.search( '\W+', data ) is not None:
            raise forms.ValidationError( '''Organization name cannot have
                                            spaces or special characters''' )

        if data in self._reserved_names:
            raise forms.ValidationError( '''Organization already exists with
                                            this name!''' )

        users = User.objects.filter( username=data )
        orgs = Organization.objects.filter( name=data )

        if len( users ) > 0 or len( orgs ) > 0:
            raise forms.ValidationError( '''Organization already exists with
                                            this name!''' )

        return data
