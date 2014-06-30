import json

from django.conf.urls import url

from tastypie.authentication import MultiAuthentication, SessionAuthentication
from tastypie.resources import Resource

from repos.models import Repository
from visualizations.models import Visualization, VisualizationSerializer

from .authentication import ApiTokenAuthentication
from .authorization import VizAuthorization


class VizResource( Resource ):

    class Meta:
        resource_name = 'viz'

        detail_allowed_methods = [ 'delete', 'get', 'post' ]

        # Ensure we have an API token before returning any data.
        # TODO: Make sure this API token concept works with public/private
        # data.
        authentication = MultiAuthentication( ApiTokenAuthentication(),
                                              SessionAuthentication() )

        authorization = VizAuthorization()

    def prepend_urls( self ):
        base_url = '^(?P<resource_name>%s)/(?P<pk>\w+)' % ( self._meta.resource_name )

        return [
            url( r'%s/(?P<viz_id>\d+)/' % ( base_url ), self.wrap_view( 'delete_detail' ), name='api_delete_detail' )
        ]

    def dehydrate( self, bundle ):
        serializer = VisualizationSerializer()
        bundle.data = serializer.serialize( [bundle.obj] )
        return bundle

    def delete_detail( self, request, **kwargs ):

        # Grab the repo we're creating a visualization for
        repo_id = kwargs.get( 'pk' )
        viz_id  = kwargs.get( 'viz_id' )

        try:
            basic_bundle = self.build_bundle( request=request )
            basic_bundle.obj = Visualization.objects.get( id=viz_id, repo__mongo_id=repo_id )

            if not self.authorized_delete_detail( basic_bundle.obj, basic_bundle ):
                return HttpUnauthorized()

            basic_bundle.obj.delete()
            response_data = { 'success': True }
            return self.create_response( request, response_data )

        except ValueError as e:
            return HttpBadRequest( str( e ) )

        return HttpUnauthorized()

    def get_detail( self, request, **kwargs ):

        # Grab the repo we're creating a visualization for
        repo_id = kwargs[ 'pk' ]

        try:
            basic_bundle = self.build_bundle( request=request )
            basic_bundle.obj = Visualization.objects.get(repo__mongo_id=repo_id)

            if not self.authorized_read_detail( basic_bundle.obj, basic_bundle ):
                return HttpUnauthorized()

            basic_bundle = self.dehydrate( basic_bundle )

            data = {
                'objects': basic_bundle.data }

            return self.create_response( request, data )
        except ValueError as e:
            return HttpBadRequest( str( e ) )

    def post_detail( self, request, **kwargs ):

        # Grab the repo we're creating a visualization for
        repo_id = kwargs[ 'pk' ]

        try:
            basic_bundle = self.build_bundle( request=request )

            repo = Repository.objects.get( mongo_id=repo_id )
            if not self.authorized_create_detail( repo, basic_bundle ):
                return HttpUnauthorized()

            params = json.loads( request.body )

            new_viz = Visualization( name=params.get( 'name' ),
                                     repo=repo,
                                     x_axis=params.get( 'x_axis' ),
                                     y_axis=params.get( 'y_axis' ) )
            new_viz.save()
            response_data = { 'success': True, 'id': str( new_viz.id ) }
            return self.create_response( request, response_data )

        except ValueError as e:
            return HttpBadRequest( str( e ) )
