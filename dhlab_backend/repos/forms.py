import json
import os
import re

from datetime import datetime

from django import forms

from pyxform.xls2json import SurveyReader
from openrosa.xform_reader import XFormReader

from backend.db import db


class NewRepoForm( forms.Form ):

    name    = forms.CharField()

    desc    = forms.CharField( widget=forms.Textarea, required=False )

    privacy = forms.ChoiceField( choices=[ ('public', 'Public'),
                                           ('private', 'Private') ],
                                 widget=forms.RadioSelect )

    survey_json     = forms.CharField( required=False,
                                       widget=forms.HiddenInput )
    xform_file      = forms.FileField( required=False )

    def __init__( self, *args, **kwargs ):

        self._user = None
        if 'user' in kwargs:
            self._user = kwargs.pop( 'user' )

        self._org = None
        if 'org' in kwargs:
            self._org = kwargs.pop( 'org' )

        super( NewRepoForm, self ).__init__( *args, **kwargs )

    def clean( self ):
        '''
            Run final checks on whether we have valid form schema to create the
            repository.
        '''
        if self.cleaned_data[ 'survey_json' ] is None and\
                self.cleaned_data[ 'xform_file' ] is None:
            raise forms.ValidationError('''Please create or upload an XForm''')

        return self.cleaned_data

    def clean_name( self ):

        data = self.cleaned_data[ 'name' ].strip()

        # Ensure form name is a valid form
        if re.search( '\W+', data ) is not None:
            raise forms.ValidationError( '''Repository name can not have
                                            spaces or special characters''' )

        # Check that this form name isn't already taken by the user
        query = { 'name': data }

        if self._user:
            query[ 'user' ] = self._user.id

        if self._org:
            query[ 'org' ] = self._org.id

        repo_exists = db.survey.find( query )

        if repo_exists.count() != 0:
            raise forms.ValidationError( '''Repository already exists with
                                            this name''' )

        return data

    def clean_survey_json( self ):
        data = self.cleaned_data[ 'survey_json' ].strip()

        if len( data ) == 0:
            return None

        # Attempt to load the into a dict
        try:
            data = json.loads( data )
        except Exception:
            return None

        return data

    def clean_xform_file( self ):

        data = self.cleaned_data[ 'xform_file' ]

        if data is None:
            return None

        name, file_ext = os.path.splitext( data.name )

        # Parse file depending on file type
        if file_ext == '.xls':
            survey = SurveyReader( data )
        elif file_ext == '.xml':
            survey = XFormReader( data )
        else:
            raise forms.ValidationError( 'Unable to read XForm' )

        return survey.to_json_dict()

    def save( self ):

        if self.cleaned_data[ 'xform_file' ]:
            repo = self.cleaned_data[ 'xform_file' ]
        else:
            repo = self.cleaned_data[ 'survey_json' ]

        print repo

        # Basic form name/description
        repo[ 'name' ] = self.cleaned_data[ 'name' ]
        repo[ 'description' ] = self.cleaned_data[ 'desc' ]

        # Needed for xform formatting
        repo[ 'title' ]       = self.cleaned_data[ 'name' ]
        repo[ 'id_string' ]   = self.cleaned_data[ 'name' ]

        # Is this form public?
        repo[ 'public' ] = self.cleaned_data[ 'privacy' ] == 'public'

        # Store who uploaded this form
        if self._user:
            repo[ 'user' ] = self._user.id

        if self._org:
            repo[ 'org' ] = self._org.id

        # Store when this form was uploaded
        repo[ 'uploaded' ]  = datetime.now()

        return repo
