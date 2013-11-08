import csv
import json
import os
import re

from django import forms
from django.utils.text import slugify

from pyxform.xls2json import SurveyReader
from openrosa.xform_reader import XFormReader

from .models import Repository


class NewBatchRepoForm( forms.Form ):

    csv_file = forms.FileField( required=True )

    FLOAT_TYPE = re.compile(r'^(\d+\.\d*|\d*\.\d+)$')
    INT_TYPE   = re.compile(r'^\d+$')

    def __init__( self, *args, **kwargs ):
        self._user = None
        if 'user' in kwargs:
            self._user = kwargs.pop( 'user' )

        self._org = None
        if 'org' in kwargs:
            self._org = kwargs.pop( 'org' )

        super( NewBatchRepoForm, self ).__init__( *args, **kwargs )

    def _sniff_type( self, val ):
        '''
            A really stupid and bare-bones approach to data type detection.
        '''
        if self.FLOAT_TYPE.match( val ):
            return 'decimal'
        elif self.INT_TYPE.match( val ):
            return 'int'
        else:
            return 'text'

    def clean( self ):
        '''
            Run through a final check before creating the new repository:

            1. Check that the name of the repo is not already taken.
        '''

        username = self._user.username if self._user else self._org.name

        if Repository.objects.repo_exists( self.cleaned_data[ 'name' ], username ):
            raise forms.ValidationError( '''Repository already exists with
                                            this name''' )

        return self.cleaned_data

    def clean_csv_file( self ):

        data = self.cleaned_data[ 'csv_file' ]

        name, file_ext = os.path.splitext( data.name )

        # Check that this is a valid CSV file...
        if file_ext != '.csv':
            raise forms.ValidationError( 'Please upload a valid CSV file' )

        csv_file = csv.reader( data )
        if csv_file is None:
            raise forms.ValidationError( 'Please upload a valid CSV file' )

        # Gleam some repo meta-data from the CSV file
        self.cleaned_data['name'] = slugify( name.strip() )
        self.cleaned_data['desc'] = 'Automatically created using %s' % ( data.name )

        # Grab the headers and create fields for the new repo
        headers = csv_file.next()
        row_one = csv_file.next()

        self.cleaned_data['headers'] = []

        for idx, header in enumerate( headers ):

            label = header.strip()

            header_info = {
                'name': slugify( unicode( label ) ),
                'label': label,
                'type': self._sniff_type( row_one[ idx ] )
            }

            self.cleaned_data[ 'headers' ].append( header_info )

        # Grab all the rows of the CSV file.
        self.cleaned_data['new_data'] = []
        datum = {}
        for idx, value in enumerate( row_one ):

            if idx >= len( self.cleaned_data[ 'headers' ] ):
                break

            datum[ self.cleaned_data[ 'headers' ][ idx ][ 'name' ] ] = value.strip()

        self.cleaned_data[ 'new_data' ].append( datum )

        for row in csv_file:
            datum = {}

            for idx, value in enumerate( row ):
                if idx >= len( self.cleaned_data[ 'headers' ] ):
                    break

                datum[ self.cleaned_data[ 'headers' ][ idx ][ 'name' ] ] = value.strip()

            self.cleaned_data[ 'new_data' ].append( datum )

        return None

    def save( self ):
        '''
            Creates a new repository using the name & data derived from the
            uploaded CSV file.
        '''
        # Use the headers to create the fields for the repo
        repo = { 'fields': self.cleaned_data[ 'headers' ] }

        # Attempt to create and save the new repository
        new_repo = Repository(
                        name=self.cleaned_data[ 'name' ],
                        description=self.cleaned_data[ 'desc' ],
                        user=self._user,
                        org=self._org,
                        is_public=False )
        new_repo.save( repo=repo )

        # Attempt to save the data from the CSV file into the repository
        for datum in self.cleaned_data[ 'new_data' ]:
            new_repo.add_data( datum, None )

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

class WebformForm( forms.Form ):
    def __init__():
        webform = Form(auto_id="%s_field")


    def setAllWithKwArgs( self, **kwargs ):
        for key, value in kwargs.items():
            setattr( self, key, value )

    def buildForm( self, in_json ):
        '''
            Build the form server-side, for webform entry
            This method is mirroring the structure of builder.coffee
            in the frontend.  This method only serves as setup for the
            recursive bulk of the code
        '''
        jsonElement = json.loads( in_json )
        #raw_template = ""
        #context_dict = {}
        for element in jsonElement:
            rawElements = buildFormTree( self, element, "/" )


    def buildFormTree( self, child, path ):
        '''
            More work for building the form server-side.
            This is only the recursive part that goes and creates
            each field.  Any prebuild code should go in buildForm above
        '''

        schema_dict = {
            'help': child.hint,
            'title': child.label,
            'is_field': True,
            'bind': child.bind,
            'tree': path
        }

        # LBYL rather than EAFP, mainly due to what we are doing
        if hasattr(child, 'relationship'):
            schema_dict['type'] = 'Text'
            schema_dict['template'] = ('<div id="%s_field" data-key="%s" class="control-group">'
                        '<label for="%s">%s</label>'
                        "<input data-repo='%s' data-field='%s'"
                            'class="autofill" type="text" name="%s">'
                    '</div>' % ( child.name, child.name, child.name, schema_dict['title'],
                    child.relationship.repo, child.relationship.field, child.name ) )

        elif child.type in ( 'string', 'text' ):
            if hasattr( child, 'bind' ) and child.bind.readonly:
                schema_dict['template'] = ('<div id="%s_field" data-key="%s" class="control-group">'
                                                        '<strong></strong>%s'
                                                   '</div>' % (child.name, child.name, schema_dict['title']))
                schema_dict['is_field'] = False

            schema_dict['type'] = 'Text'

        elif child.type in ( 'decimal', 'int', 'integer' ):
            schema_dict['template'] = ('<div id="%s_field" data-key="%s" class="control-group">'
                                                        '<label class="control-label" for="%s">%s</label>'
                                                        '<div class="controls">'
                                                            '<span data-editor>'
                                                                '<input id="%s" name="%s" type="number" step="any">'
                                                            '</span>'
                                                            '<div class="help-inline" data-error></div>'
                                                            '<div class="help-block">'
                                                        '</div>'
                                                   '</div>' % (child.name, child.name, child.name,
                                                    schema_dict['title'], child.name, child.name))

            schema_dict['type'] = 'Numeric'

        elif child.type == 'date':
            pass

        elif child.type in ( 'time', 'datetime' ):
            pass

        elif child.type == 'today':
            pass

        # Geographical data type to field
        elif child.type == 'geopoint':
            schema_dict['template'] = ('<div id="%s_field" data-key="%s" class="control-group">'
                                            '<strong></strong>%s<br>'
                                            '<input id="%s" type="hidden" name="%s" >'
                                            '<div id="%s_map" style="width:100%; height: 500px; position: relative;"></div>'
                                       '</div>' % (child.name, child.name, schema_dict['title'],
                                                   child.name, child.name, child.name))

            schema_dict['bind'] = 'map'

        elif child.type == 'trigger':
            pass

        # Advisement text to field
        elif child.type == 'note':
            schema_dict['template'] = ('<div id="%s_field" data-key="%s" class="control-group">'
                                            '%s'
                                       '</div>' % (child.name, child.name, schema_dict['title']))

            schema_dict['type'] = 'Text'
            schema_dict['is_field'] = False

        # All media types
        elif child.type == 'photo':
            schema_dict['template'] = ('<div id="%s_field" data-key="%s" class="control-group">'
                                            '<label for="%s">%s</label>'
                                            '<input type="file" name="%s" accept="image/*"></input>'
                                       '</div>' % (child.name, child.name, child.name, 
                                                   schema_dict['title'], child.name))

            schema_dict['type'] = 'Text'


        elif child.type == 'video':
            schema_dict['template'] = ('<div id="%s_field" data-key="%s" class="control-group">'
                                            '<label for="%s">%s</label>'
                                            '<input type="file" name="%s" accept="video/*"></input>'
                                       '</div>' % (child.name, child.name, child.name,
                                                   schema_dict['title'], child.name))

            schema_dict['type'] = 'Text'

        # selections.  Generation of selections happens in another method.
        elif child.type == 'select all that apply':
            pass

        elif child.type == "select one":
            pass

        # Woo!  MORE Recursion!  
        # TODO: I'll take care of this later, don't want to handle recursion logic right now
        elif child.type == 'group':
            pass

        elif child.type == 'calculate':
            pass

        #return raw_html, schema_dict


        # TODO: double-check the JSON to see if this format is correct

    '''
        Meant for select multiple and select one
        For preparation of the choices for the question
    '''
    def prepChoices ( self, choices ):
        pass

