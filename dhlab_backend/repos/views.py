import json
import math
import os

from bson import ObjectId
from datetime import datetime
from numpy import linspace

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from backend.db import db, dehydrate_survey
from privacy.map import privatize

from pyxform.xls2json import SurveyReader
from openrosa.xform_reader import XFormReader

from .forms import NewRepoForm, BuildRepoForm


@login_required
def new_repo( request ):
    '''
        Creates a new user under the currently logged in user.
    '''
    # Handle XForm upload
    if request.method == 'POST':

        form = NewRepoForm( request.POST, request.FILES )

        # Check for a valid XForm and parse the file!
        if form.is_valid():

            # Additional errors we may encounter
            has_errors = False

            # Check that this form name isn't already taken by the user
            form_exists = db.survey.find( { 'name': form.cleaned_data['name'],
                                            'user': request.user.id } )

            if form_exists.count() != 0:
                errors = form._errors.setdefault( 'name', ErrorList() )
                errors.append( 'Repository already exists with this name' )
                has_errors = True

            # Parse form file
            survey = None
            if not has_errors:
                # Detect whether this is an XLS or XML file.
                xform_file = request.FILES['xform_file']
                name, file_ext = os.path.splitext( xform_file.name)

                # Parse file depending on file type
                if file_ext == '.xls':
                    survey = SurveyReader( xform_file )
                elif file_ext == '.xml':
                    survey = XFormReader( xform_file )
                else:
                    errors = form._errors.setdefault('xform_file', ErrorList())
                    errors.append( 'Unable to load XForm' )
                    has_errors = True

            # Create repo!
            if survey and not has_errors:
                data = survey.to_json_dict()

                # Basic form name/description
                data[ 'name' ] = form.cleaned_data[ 'name' ]
                data[ 'description' ] = form.cleaned_data[ 'desc' ]

                # Needed for xform formatting
                data[ 'title' ]       = form.cleaned_data[ 'name' ]
                data[ 'id_string' ]   = form.cleaned_data[ 'name' ]

                # Is this form public?
                data[ 'public' ] = form.cleaned_data[ 'privacy' ] == 'public'

                # Store who uploaded this form
                data[ 'user' ]      = request.user.id

                # Store when this form was uploaded
                data[ 'uploaded' ]  = datetime.now()

                db.survey.insert( data )

                return HttpResponseRedirect( '/' )

    else:
        form = NewRepoForm()

    return render_to_response( 'new.html', { 'form': form },
                               context_instance=RequestContext(request) )


@login_required
def build_form( request ):
    '''
        Builds form.
        '''
    # Handle XForm upload
    if request.method == 'POST':

        form = BuildRepoForm( request.POST )

        # Check for a valid XForm and parse the file!
        if form.is_valid():

            # Check that this form name isn't already taken by the user
            form_exists = db.survey.find( { 'name': form.cleaned_data['name'],
                                            'user': request.user.id } )

            if form_exists.count() != 0:
                errors = form._errors.setdefault( 'name', ErrorList() )
                errors.append( 'Repository already exists with this name' )
            else:

                data = json.loads(request.POST['surveyjson'])

                # Basic form name/description
                data[ 'name' ] = form.cleaned_data[ 'name' ]
                data[ 'description' ] = form.cleaned_data[ 'desc' ]

                # Needed for xform formatting
                data[ 'title' ]       = form.cleaned_data[ 'name' ]
                data[ 'id_string' ]   = form.cleaned_data[ 'name' ]

                # Is this form public?
                data[ 'public' ] = form.cleaned_data[ 'privacy' ] == 'public'

                # Store who uploaded this form
                data[ 'user' ]      = request.user.id

                data[ 'type' ]      = 'survey'

                # Store when this form was uploaded
                data[ 'uploaded' ]  = datetime.now()

                print data

                db.survey.insert( data )

                return HttpResponseRedirect( '/' )
        else:
            print "form is not valid"

    else:
        form = BuildRepoForm()

    return render_to_response( 'build_form.html', { 'form': form },
                               context_instance=RequestContext(request) )


@login_required
def delete_repo( request, repo_id ):
    '''
        Delete a data repository.

        Checks if the user is the original owner of the repository and removes
        the repository and the accompaning repo data.
    '''

    survey = db.survey.find_one( { '_id': ObjectId( repo_id ) },
                                 { 'user': True } )

    if survey[ 'user' ] != request.user.id:
        return HttpResponse( 'Unauthorized', status=401 )

    db.survey.remove( { '_id': ObjectId( repo_id ) } )
    db.data.remove( { 'repo': ObjectId( repo_id ) } )

    return HttpResponseRedirect( '/' )


@csrf_exempt
@require_POST
@login_required
def toggle_public( request, repo_id ):
    '''
        Toggle's a data repo's "publicness". Only the person who owns the form
        is allowed to make such changes to the form settings.
    '''

    # Find a survey, only looking for the user field
    survey = db.survey.find_one( { '_id': ObjectId( repo_id ) },
                                 { 'user': True, 'public': True } )

    # Check if the owner of the survey matches the user who is logged in
    if survey[ 'user' ] != request.user.id:
        return HttpResponse( 'Unauthorized', status=401 )

    if 'public' in survey:
        survey[ 'public' ] = not survey[ 'public' ]
    else:
        survey[ 'public' ] = True

    db.survey.update( { '_id': ObjectId( repo_id ) },
                      { '$set': { 'public': survey[ 'public' ] } } )

    return HttpResponse( json.dumps( { 'success': True,
                                       'public': survey[ 'public' ] } ),
                         mimetype='application/json' )


@require_GET
def webform( request, username, repo_name ):
    '''
        Simply grab the survey data and send it on the webform. The webform
        will handle rendering and submission of the final data to the server.
    '''
    user = get_object_or_404( User, username=username )

    repo = db.survey.find_one( { 'name': repo_name, 'user': user.id } )

    if repo is None:
        return HttpResponse( status=404 )

    repo_user = get_object_or_404( User, id=repo[ 'user' ] )

    return render_to_response( 'get.html',
                               { 'repo': repo,
                                 'repo_user': repo_user,
                                 'repo_id': str( repo[ '_id' ] ) },
                               context_instance=RequestContext( request ))


@require_GET
def repo_viz( request, username, repo_name ):
    '''
        View repo <repo_name> under user <username>.

        Does the checks necessary to determine whether the current user has the
        authority to view the current repository.
    '''

    user = get_object_or_404( User, username=username )

    # Looking our own viz or someone's public repo?
    is_other_user = request.user.username != username

    repo = db.survey.find_one({ 'name': repo_name, 'user': user.id })

    if repo is None:
        return HttpResponse( status=404 )

    # Check to see if the user has access to view this survey
    if not repo.get( 'public', False ) and is_other_user:
        return HttpResponse( 'Unauthorized', status=401 )

    # Grab the data for this repository
    data = db.data.find( {'repo': ObjectId( repo[ '_id' ] )} )
    data = dehydrate_survey( data )

    # Is some unknown user looking at this data?
    if is_other_user:
        # Does this data have any geo data?
        has_geo = False
        geo_index = None
        for field in repo[ 'children' ]:
            if field[ 'type' ] == 'geopoint':
                has_geo = True
                geo_index = field[ 'name' ]
                break

        # Great! We have geopoints, let's privatize this data
        if has_geo:
            xbounds     = [ None, None ]
            ybounds     = [ None, None ]
            fuzzed_data = []

            for datum in data:

                geopoint = datum[ 'data' ][ geo_index ].split( ' ' )

                try:
                    point = ( float( geopoint[0] ), float( geopoint[1] ) )
                except ValueError:
                    continue

                if xbounds[0] is None or point[0] < xbounds[0]:
                    xbounds[0] = point[0]

                if xbounds[1] is None or point[0] > xbounds[1]:
                    xbounds[1] = point[0]

                if ybounds[0] is None or point[1] < ybounds[0]:
                    ybounds[0] = point[1]

                if ybounds[1] is None or point[1] > ybounds[1]:
                    ybounds[1] = point[1]

                fuzzed_data.append( point )

            # Split the xbounds in a linear
            num_x_samples = int(math.ceil( ( xbounds[1] - xbounds[0] ) / .2 ))
            num_y_samples = int(math.ceil( ( ybounds[1] - ybounds[0] ) / .2 ))

            xbounds = linspace( xbounds[0], xbounds[1], num=num_x_samples )
            ybounds = linspace( ybounds[0], ybounds[1], num=num_y_samples )

            fuzzed_data = privatize( points=fuzzed_data,
                                     xbounds=xbounds,
                                     ybounds=ybounds )
            data = []
            for datum in fuzzed_data:
                data.append( {
                    'data':
                    {geo_index: ' '.join( [ str( x ) for x in datum ] )}})

    return render_to_response( 'visualize.html',
                               { 'repo': repo,
                                 'sid': repo[ '_id' ],
                                 'data': json.dumps( data ),
                                 'is_other_user': is_other_user,
                                 'account': user},
                               context_instance=RequestContext(request) )


@require_GET
def map_visualize( request ):
    return render_to_response( 'map_visualize.html',
                               context_instance=RequestContext(request) )
