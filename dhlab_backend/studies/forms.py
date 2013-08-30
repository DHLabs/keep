from django import forms

#from repos.models import Repository

from .models import Study


class NewStudyForm( forms.Form ):
    '''
        Validates and creates a new study.
    '''

    name = forms.CharField()
    description = forms.CharField( required=False )
    tracker = forms.BooleanField( required=False )

    def clean_name( self ):
        return self.cleaned_data[ 'name' ].strip()

    def clean_description( self ):
        return self.cleaned_data[ 'description' ].strip()

    def save( self, user, org=None ):
        '''
            Save and return the new study. Should only be called if there are
            no errors in the form.

            Params
            ------
            user : User : required
                The currently logged in user who is this study is for.

            org : Organization : optional
                If a user is creating a study as part of an organization, this
                will be set.
        '''
        if not self.is_valid():
            return None

        new_study = Study( name=self.cleaned_data[ 'name' ],
                           description=self.cleaned_data[ 'description' ],
                           user=user,
                           org=org )
        new_study.save()

        # If the user wants a way to track things using this study, we'll create
        # a special "registration" type repository.

        return new_study
