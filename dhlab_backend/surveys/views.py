import json
from bson import ObjectId

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from backend.db import db, dehydrate_survey


@require_POST
def delete_form( request, form_id ):

    survey = db.survey.find_one( { '_id': ObjectId( form_id ) },
                                 { 'user': True } )

    if survey[ 'user' ] != request.user.id:
        return HttpResponse( 'Unauthorized', status=401 )

    db.survey.remove( { '_id': ObjectId( form_id ) } )
    db.survey_data.remove( { 'survey': ObjectId( form_id ) } )

    return HttpResponseRedirect( '/dashboard' )


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
    return render_to_response( 'forms/get.html',
                               { 'form': data,
                                 # Convert the form id to a string for easy
                                 # access
                                 'form_id': str( data[ '_id' ] ) } )


@require_GET
def visualize( request, username, form_id ):

    user = User.objects.get(username=username)

    data = db.survey_data.find( {'survey': ObjectId( form_id )} )
    form = db.survey.find_one( { '_id': ObjectId( form_id ), 'user': user.id } )


    # Check to see if the user has access to view this survey
    if not form.get( 'public', False ):
        if request.user.id is None or request.user.id != form[ 'user' ]:
            return HttpResponse( 'Unauthorized', status=401 )

    return render_to_response( 'visualize.html',
                               { 'survey': form,
                                 'sid': form[ '_id' ],
                                 'data': json.dumps( dehydrate_survey(data) )},
                               context_instance=RequestContext(request) )


@require_GET
def map_visualize( request ):
    return render_to_response( 'map_visualize.html',
                               context_instance=RequestContext(request) )
