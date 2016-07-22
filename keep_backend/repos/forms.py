import csv
import json
import os
import re

from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage as storage
from django.utils.text import slugify

from pyxform.xls2json import SurveyReader
from openrosa.xform_reader import XFormReader

from .models import Repository
from api.tasks import create_repo_from_file
from studies.models import Study


class NewBatchRepoForm( forms.Form ):
    '''
        Create a new repo from a CSV file.
    '''
<<<<<<< HEAD

=======
    print "in NewBatchRepoForm class in /repos/forms.py"
>>>>>>> 11d6f5f3f8fe3840e38a1cf13df3b1430a92602e
    # File used to create/populate the new repo
    repo_file   = forms.FileField( required=True )
    # The study this repo is associated with
    study       = forms.IntegerField( required=False )
    # Whether or not this repo is a "tracker" repo.
    tracker     = forms.BooleanField( required=False )

    VALID_FILE_TYPES = [ 'csv', 'xml', 'xls' ]

    def __init__( self, *args, **kwargs ):
        self._user = None
        if 'user' in kwargs:
            self._user = kwargs.pop( 'user' )

        self._org = None
        if 'org' in kwargs:
            self._org = kwargs.pop( 'org' )
<<<<<<< HEAD

=======
        print " in NewBatchRepoForm/__init__ "
>>>>>>> 11d6f5f3f8fe3840e38a1cf13df3b1430a92602e
        super( NewBatchRepoForm, self ).__init__( *args, **kwargs )

    def clean( self ):
        '''
            Run through a final check before creating the new repository:

            1. Check that the name of the repo is not already taken.
        '''

        username = self._user.username if self._user else self._org.name

        if Repository.objects.repo_exists( self.cleaned_data[ 'name' ], username ):
            raise forms.ValidationError( 'Repository already exists with this name' )
<<<<<<< HEAD

=======
        print " in NewBatchRepoForm clean "
>>>>>>> 11d6f5f3f8fe3840e38a1cf13df3b1430a92602e
        return self.cleaned_data

    def clean_study( self ):
        '''
            Check if the study id that was passed in refers to a valid study.

            1. The study must exist
            2. The user must have access to this study.
        '''

        data = self.cleaned_data[ 'study' ]
        if data == None:
            return data

        try:
            study = Study.objects.get( id=data, user=self._user )
        except ObjectDoesNotExist:
            raise forms.ValidationError( 'Invalid study' )
<<<<<<< HEAD

=======
        print " in clean_study "
>>>>>>> 11d6f5f3f8fe3840e38a1cf13df3b1430a92602e
        return study

    def clean_repo_file( self ):
        '''
            Determine the file type and check it against our list of valid file
            types.
        '''

        data = self.cleaned_data[ 'repo_file' ]

        # Split apart the file name so we can attempt to detect the file type
        name, file_ext = os.path.splitext( data.name )
        file_ext = file_ext[1:].lower()

        # Check that this is a valid CSV file...
        if file_ext not in self.VALID_FILE_TYPES:
            raise forms.ValidationError( 'Please upload a valid CSV, XML, or XLS file' )

        # Gleam some repo meta-data from the file
        self.cleaned_data[ 'file_ext' ] = file_ext
        self.cleaned_data[ 'name' ] = slugify( name.strip() )
        self.cleaned_data[ 'desc' ] = 'Automatically created using %s' % ( data.name )
<<<<<<< HEAD

=======
        print "in forms/clean_repo_file "
>>>>>>> 11d6f5f3f8fe3840e38a1cf13df3b1430a92602e
        return self.cleaned_data[ 'repo_file' ]

    def save( self ):
        '''
            Creates a new repository and creates a task to parse the file that
            was uploaded by the user.

            The task will handle the parsing and addition of fields and data
            into the repository.
        '''
<<<<<<< HEAD

=======
	    #print ("in repos/forms save") 
>>>>>>> 11d6f5f3f8fe3840e38a1cf13df3b1430a92602e
        # For now, the repository will have an empty field list.
        repo = { 'fields': [] }

        # Attempt to create and save the new repository
        new_repo = Repository(
                        name=self.cleaned_data[ 'name' ],
                        study=self.cleaned_data[ 'study' ],
                        description=self.cleaned_data[ 'desc' ],
                        is_tracker=self.cleaned_data[ 'tracker' ],
                        user=self._user,
                        org=self._org,
                        is_public=False )
<<<<<<< HEAD
=======
        print ("in repos/forms going to save repo in repos forms")
        print("repo is: ")
        print repo

>>>>>>> 11d6f5f3f8fe3840e38a1cf13df3b1430a92602e
        new_repo.save( repo=repo )

        # Save the file to our storage bucket to be processed ASAP.
        if not settings.DEBUG and not settings.TESTING:
            storage.bucket_name = settings.AWS_TASK_STORAGE_BUCKET_NAME
<<<<<<< HEAD

        s3_url = '%s.%s' % ( new_repo.mongo_id, self.cleaned_data[ 'file_ext' ] )
        storage.save( s3_url, self.cleaned_data[ 'repo_file' ] )

        # Create a task and go!
        task = create_repo_from_file.delay( file=s3_url,
                                            file_type=self.cleaned_data[ 'file_ext' ],
                                            repo=new_repo.mongo_id )
=======
	
	    print ("in repos forms, settings.DEBUG is: ")
	    print settings.DEBUG
        s3_url = '%s.%s' % ( new_repo.mongo_id, self.cleaned_data[ 'file_ext' ] )
        print("in repos forms going to storage.save")
        print ("s3_url is:")
        print s3_url
        print ("self.cleaned_data is:")
        print self.cleaned_data[ 'repo_file' ] 
        print self.cleaned_data[ 'name' ], self.cleaned_data[ 'study' ],self.cleaned_data[ 'desc' ], self.cleaned_data[ 'tracker' ]
        
        storage.save( s3_url, self.cleaned_data[ 'repo_file' ] )

        # Create a task and go!
        
        task = create_repo_from_file.delay( file=s3_url,
                                            file_type=self.cleaned_data[ 'file_ext' ],
                                            repo=new_repo.mongo_id ) 
>>>>>>> 11d6f5f3f8fe3840e38a1cf13df3b1430a92602e
        new_repo.add_task( task.task_id, 'create_repo' )

        return new_repo


class NewRepoForm( forms.Form ):
    """Validates and creates a new repository based on creation data.

       Parameters
       ----------
       forms.Form : Form

       Attributes
       ----------
       name : string
           name of the form
       desc : string
           description of the form
       privacy
       survey_json : string, optional
           The JSON of the form as a string, only if creating
           a form from scratch
       xform_file : File, optional
           Generally, the csv/xform that we are creating a repository
           from.

    """

    name    = forms.CharField()

    desc    = forms.CharField( widget=forms.Textarea(attrs={'rows':5,'class':'input-xxlarge'} ), required=False )

    privacy = forms.ChoiceField( choices=[ ('public', 'Public'),
                                           ('private', 'Private') ],
                                 widget=forms.RadioSelect )

    survey_json     = forms.CharField( required=False,
                                       widget=forms.HiddenInput )
    xform_file      = forms.FileField( required=False )

    def __init__( self, *args, **kwargs ):
        """We pass in the current user/org to test for the uniqueness of
           the repository name in that current user's/org's list of
           repositories.

           Params
           ------
           user : User

           org : Organization, optional
               If a user is acting on behalf of an organization,
               this needs to be set.
        """

        self._user = None
        if 'user' in kwargs:
            self._user = kwargs.pop( 'user' )

        self._org = None
        if 'org' in kwargs:
            self._org = kwargs.pop( 'org' )

        super( NewRepoForm, self ).__init__( *args, **kwargs )

    def clean( self ):
        """
            Run final checks on whether we have valid form schema to create the
            repository.
        """
        if self.cleaned_data[ 'survey_json' ] is None and\
                self.cleaned_data[ 'xform_file' ] is None:
            raise forms.ValidationError('''Please create or upload an XForm''')

        return self.cleaned_data

    def clean_name( self ):
        """
            Clean & checks for the validity of the repo name.

            1. Strip the repo name of any whitespace.
            2. Check to see if the form name is a valid form name.
            3. Check to see if the form name is not already taken by the user.

            See http://docs.python.org/2/library/re.html for more info on the
            regexes used.
        """

        data = self.cleaned_data[ 'name' ].strip()

        # Ensure form name is a valid form
        if re.search( '[^-a-zA-Z0-9_]', data ) is not None:
            raise forms.ValidationError( '''Repository name can not have
                                            spaces or special characters''' )

        # Check that this form name isn't already taken by the user
        username = self._org.name if self._org else self._user.username
        if Repository.objects.repo_exists( data, username ):
            raise forms.ValidationError( '''Repository already exists with
                                            this name''' )

        return data

    def clean_survey_json( self ):
        """
            Clean & checks the validity of the repo JSON representation.
        """

        data = self.cleaned_data[ 'survey_json' ].strip()

        if len( data ) == 0:
            return None

        # Attempt to load the into a dict
        try:
            data = json.loads( data )
        except Exception:
            return None

        # Add a default language
        data[ 'default_language' ] = 'default'

        # Go through and remove fields that dont have a valid label
        to_remove = []
        for field in data[ 'children' ]:
            if len( field[ 'label' ] ) == 0 or len( field[ 'name' ] ) == 0:
                to_remove.append( field )

        # Delete fields.
        for el in to_remove:
            data[ 'children' ].remove( el )

        return data

    def clean_xform_file( self ):
        """
            Clean & checks the validity of the uploaded xform file.
        """

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
        """
            If everything is in place, attempt to save the new repository to
            MongoDB & our database.
        """
<<<<<<< HEAD

=======
        print "in save "
>>>>>>> 11d6f5f3f8fe3840e38a1cf13df3b1430a92602e
        repo = {}
        if self.cleaned_data[ 'xform_file' ]:
            repo['fields'] = self.cleaned_data[ 'xform_file' ]['children']
            repo['type'] = "survey"
        else:
            repo['fields'] = self.cleaned_data[ 'survey_json' ]['children']
            repo['type'] = self.cleaned_data[ 'survey_json' ]['type']

        # Needed for xform formatting
        # repo[ 'title' ]       = self.cleaned_data[ 'name' ]
        # repo[ 'id_string' ]   = self.cleaned_data[ 'name' ]

        new_repo = Repository(
                        name=self.cleaned_data[ 'name' ],
                        description=self.cleaned_data[ 'desc' ],
                        user=self._user,
                        org=self._org,
                        is_public=self.cleaned_data[ 'privacy' ] == 'public' )
        return new_repo.save( repo=repo )
