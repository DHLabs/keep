from django import forms
from django.utils.text import slugify

from repos.models import Repository

from .models import Study


class NewStudyForm( forms.Form ):
    """
        Validates and creates a new study.
    """

    name = forms.CharField()
    description = forms.CharField( required=False )
    tracker = forms.BooleanField( required=False )

    def clean_name( self ):
        return self.cleaned_data[ 'name' ].strip()

    def clean_description( self ):
        return self.cleaned_data[ 'description' ].strip()

    def save( self, user, org=None ):
        """
            Save and return the new study. Should only be called if there are
            no errors in the form.

            Params
            ------
            user : User : required
                The currently logged in user who is this study is for.

            org : Organization : optional
                If a user is creating a study as part of an organization, this
                will be set.
        """
        if not self.is_valid():
            return None

        kwargs = { 'name': self.cleaned_data[ 'name' ],
                   'description': self.cleaned_data[ 'description' ],
                   'user': user,
                   'org': org }

        # Set the "tracker" field if the user wants to start off tracking
        # objects.
        if self.cleaned_data[ 'tracker' ]:
            kwargs[ 'tracker' ] = 'id'

        new_study = Study( **kwargs )
        new_study.save()

        if self.cleaned_data[ 'tracker' ]:
            # If the user wants a way to track things using this study, we'll create
            # a special "registration" type repository.

            repo_fields = { 'fields': [] }

            # Add a generic "name" field.
            repo_fields[ 'fields' ].append( { 'bind': { 'required': 'yes' },
                                              'label': 'Name',
                                              'name': 'name',
                                              'type': 'text' } )

            # Add the id field
            repo_fields[ 'fields' ].append( { 'bind': { 'required': 'yes','calculate':'' },
                                              'label': new_study.tracker,
                                              'name': new_study.tracker,
                                              'type': 'calculate' } )

            repo_name = '%s-tracker' % ( slugify( new_study.name.lower() ) )
            repo_desc = 'Created to track objects for the %s study' % ( new_study.name )

            # Attempt to create new repository.
            new_repo = Repository( name=repo_name,
                                   description=repo_desc,

                                   user=new_study.user,
                                   org=new_study.org,

                                   is_tracker=True,
                                   study=new_study )

            new_repo.save( repo=repo_fields )

        return new_study
