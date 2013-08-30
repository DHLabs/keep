import json

from tastypie.authentication import MultiAuthentication, SessionAuthentication
from tastypie.authorization import Authorization
from tastypie.http import HttpUnauthorized, HttpBadRequest
from tastypie.resources import ModelResource

from studies.forms import NewStudyForm
from studies.models import Study

from .authentication import ApiTokenAuthentication


class StudyAuthorization( Authorization ):

    def create_list( self, object_list, bundle ):
        '''
            By default, a user has the ability to add studies for themselves.
        '''
        return True

    def delete_detail( self, object_list, bundle ):
        '''
            Does a user have the ability to delete the selected study?
        '''
        return bundle.request.user.has_perm( 'delete_study', bundle.obj )

    def update_detail( self, object_list, bundle ):
        '''
            Does a user have the ability to edit the selected study?
        '''
        return bundle.request.user.has_perm( 'change_study', bundle.obj )


class StudyResource( ModelResource ):
    class Meta:
        queryset = Study.objects.all()
        resource_name = 'studies'

        list_allowed_methods = [ 'get', 'post' ]
        detail_allowed_methods = [ 'get', 'delete' ]

        authentication = MultiAuthentication( SessionAuthentication(), ApiTokenAuthentication() )
        authorization = StudyAuthorization()

    def dehydrate( self, bundle ):
        bundle.data['user'] = bundle.obj.user
        return bundle

    def post_list( self, request, **kwargs ):

        # First and foremost, ensure that the user is logged in and valid.
        logged_in_user = request.user

        if logged_in_user.is_anonymous():
            return HttpUnauthorized()

        # Convert new study data into a python dictionary. If we receive some
        # error converting the data into a dictionary, return a HttpBadRequest.
        try:
            params = json.loads( request.body )
        except Exception:
            return HttpBadRequest()

        # Validate the data passed into the form
        form = NewStudyForm( params )
        if not form.is_valid():
            return HttpBadRequest()

        new_study = form.save( user=logged_in_user )

        response_data = { 'success': True, 'id': new_study.id }
        return self.create_response( request, response_data )
