import json

from bson import ObjectId
from datetime import datetime

from django.contrib.auth.models import User
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from backend.db import db, dehydrate_survey

from pyxform.xls2json import SurveyReader

from .forms import NewRepoForm


def new_repo( request ):
    # Handle XForm upload
    if request.method == 'POST':

        form = NewRepoForm( request.POST, request.FILES )

        # Check for a valid XForm and parse the file!
        if form.is_valid():

            # Check that this form name isn't already taken by the user
            form_exists = db.survey.find( { 'name': form.cleaned_data['name'],
                                            'user': request.user.id } )

            if form_exists is not None:
                errors = form._errors.setdefault( 'name', ErrorList() )
                errors.append( 'Repository already exists with this name' )
            else:
                # Parse the file and store into our database
                survey = SurveyReader( request.FILES[ 'xform_file' ] )

                if len( survey._warnings ) > 0:
                    print 'Warnings parsing xls file!'

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

                #db.survey.insert( data )

                return HttpResponseRedirect( '/' )

    else:
        form = NewRepoForm()

    return render_to_response( 'new.html', { 'form': form },
                               context_instance=RequestContext(request) )


def delete_form( request, form_id ):

    survey = db.survey.find_one( { '_id': ObjectId( form_id ) },
                                 { 'user': True } )

    if survey[ 'user' ] != request.user.id:
        return HttpResponse( 'Unauthorized', status=401 )

    db.survey.remove( { '_id': ObjectId( form_id ) } )
    db.survey_data.remove( { 'survey': ObjectId( form_id ) } )

    return HttpResponseRedirect( '/' )


@csrf_exempt
@require_POST
def toggle_public( request, form_id ):
    '''
        Toggle's a data repo's "publicness". Only the person who owns the form
        is allowed to make such changes to the form settings.
    '''

    # Find a survey, only looking for the user field
    survey = db.survey.find_one( { '_id': ObjectId( form_id ) },
                                 { 'user': True, 'public': True } )

    # Check if the owner of the survey matches the user who is logged in
    if survey[ 'user' ] != request.user.id:
        return HttpResponse( 'Unauthorized', status=401 )

    if 'public' in survey:
        survey[ 'public' ] = not survey[ 'public' ]
    else:
        survey[ 'public' ] = True

    db.survey.update( { '_id': ObjectId( form_id ) },
                      { '$set': { 'public': survey[ 'public' ] } } )

    return HttpResponse( json.dumps( { 'success': True,
                                       'public': survey[ 'public' ] } ),
                         mimetype='application/json' )


@require_GET
def webform( request, form_id ):
    '''
        Simply grab the survey data and send it on the webform. The webform
        will handle rendering and submission of the final data to the server.
    '''
    data = db.survey.find_one( { '_id': ObjectId( form_id ) } )
    return render_to_response( 'get.html',
                               { 'form': data,
                                 # Convert the form id to a string for easy
                                 # access
                                 'form_id': str( data[ '_id' ] ) } )


@require_GET
def visualize( request, username, form_id ):

    user = User.objects.get(username=username)

    data = db.survey_data.find( {'survey': ObjectId( form_id )} )
    repo = db.survey.find_one({ '_id': ObjectId( form_id ), 'user': user.id })

    if repo is None:
        return HttpResponse( status=404 )

    # Check to see if the user has access to view this survey
    if not repo.get( 'public', False ):
        if request.user.id is None or request.user.id != repo[ 'user' ]:
            return HttpResponse( 'Unauthorized', status=401 )

    return render_to_response( 'visualize.html',
                               { 'repo': repo,
                                 'sid': repo[ '_id' ],
                                 'data': json.dumps( dehydrate_survey(data) ),
                                 'account': user},
                               context_instance=RequestContext(request) )


@require_GET
def map_visualize( request ):
    return render_to_response( 'map_visualize.html',
                               context_instance=RequestContext(request) )
