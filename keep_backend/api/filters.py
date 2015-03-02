from django.contrib.auth.models import User

from tastypie.resources import ModelResource
from tastypie import fields

from api.authorization import UserObjectsOnlyAuthorization
from api.repo import RepoResource
from visualizations.models import FilterSet
from repos.models import Repository

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['id', 'username']

class FilterSetResource(ModelResource):

    class Meta:
        always_return_data = True # need to set id after POST in Backbone
        queryset = FilterSet.objects.all()
        resource_name = 'filters' # endpoint is /api/v1/filters/
        authorization = UserObjectsOnlyAuthorization()
        fields = ['id', 'user', 'repo', 'name', 'querystring']
        filtering = {
            'repo': ('exact'),
            'user': ('exact')
        }

    def dehydrate(self, bundle):
        bundle.data['user'] = bundle.obj.user.id
        bundle.data['repo'] = bundle.obj.repo.id
        return bundle

    def hydrate(self, bundle):
        bundle.obj.user = User.objects.get(id=bundle.data['user'])
        bundle.obj.repo = Repository.objects.get(id=bundle.data['repo'])
        return bundle
