from tastypie.authentication import MultiAuthentication, SessionAuthentication, Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest
from tastypie.http import HttpUnauthorized, HttpNotFound
from tastypie.resources import ModelResource

from studies.models import Study

from .authentication import ApiTokenAuthentication


class StudyAuthorization( Authorization ):
    def update_list( self, object_list, bundle ):
        print object_list

        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)

        return allowed


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

        logged_in_user = request.user
        print logged_in_user

        response_data = { 'success': True, 'id': '1' }
        return self.create_response( request, response_data )
