import json

from guardian.shortcuts import get_perms

from tastypie.authentication import MultiAuthentication, SessionAuthentication
from tastypie.authorization import Authorization
from tastypie.http import HttpUnauthorized
from tastypie.resources import ModelResource

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

        params = json.loads( request.body )

        params[ 'name' ] = params.get( 'name', '' ).strip()
        params[ 'description' ] = params.get( 'description', '' ).strip()

        if len( params[ 'name' ] ) == 0:
            return HttpUnauthorized()

        logged_in_user = request.user

        if logged_in_user.is_anonymous():
            return HttpUnauthorized()

        new_study = Study( name=params[ 'name' ],
                           description=params[ 'description' ],
                           user=logged_in_user,
                           org=None )
        #new_study_id = new_study.save()

        # If the user wants a way to track things using this study, we'll create
        # a special "registration" type repository.

        new_study_id = 1
        response_data = { 'success': True, 'id': new_study_id }
        return self.create_response( request, response_data )
