import re

from django import forms
from django.forms.util import ErrorList


class NewRepoForm( forms.Form ):

    name    = forms.CharField()

    desc    = forms.CharField( widget=forms.Textarea, required=False )

    privacy = forms.ChoiceField( choices=[ ('public', 'Public'),
                                           ('private', 'Private') ],
                                 widget=forms.RadioSelect )

    xform_file      = forms.FileField()

    def clean( self ):
        if any( self.errors ):
            return

        # Ensure form name is a valid form
        if re.search( '\W+', self.cleaned_data[ 'name' ] ) is not None:

            errors = self._errors.setdefault( "name", ErrorList() )
            errors.append( '''Repository name can not have
                              spaces or special characters''' )

        return self.cleaned_data

class BuildRepoForm( forms.Form ):

    name    = forms.CharField()

    desc    = forms.CharField( widget=forms.Textarea, required=False )

    privacy = forms.ChoiceField( choices=[ ('public', 'Public'),
                                          ('private', 'Private') ],
                                widget=forms.RadioSelect )

    def clean( self ):
        if any( self.errors ):
            return

        # Ensure form name is a valid form
        if re.search( '\W+', self.cleaned_data[ 'name' ] ) is not None:

            errors = self._errors.setdefault( "name", ErrorList() )
            errors.append( '''Repository name can not have
                spaces or special characters''' )
        
        return self.cleaned_data
