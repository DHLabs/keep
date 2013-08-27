import json

from tastypie.authentication import MultiAuthentication, SessionAuthentication
from tastypie.authorization import Authorization
from tastypie.http import HttpUnauthorized
from tastypie.resources import ModelResource

from studies.models import Study

from .authentication import ApiTokenAuthentication


class StudyAuthorization( Authorization ):

    def create_list( self, object_list, bundle ):
        print 'create list'
        return True

    def create_detail( self, object_list, bundle ):
        print 'create_detail'
        return True

    def update_detail( self, object_list, bundle ):
        print 'update_detail'
        return True

    def update_list( self, object_list, bundle ):
        print 'CALLED'

        print object_list

        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)

        return True


class StudyResource( ModelResource ):
    class Meta:
        queryset = Study.objects.all()
        resource_name = 'studies'

        list_allowed_methods = [ 'get', 'post' ]
        detail_allowed_methods = [ 'get' ]

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
        new_study_id = new_study.save()
        response_data = { 'success': True, 'id': new_study_id }
        return self.create_response( request, response_data )
