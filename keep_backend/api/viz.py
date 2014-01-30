import json

from tastypie.authentication import MultiAuthentication, SessionAuthentication
from tastypie.resources import Resource

from repos.models import Repository
from visualizations.models import Visualization, VisualizationSerializer

from .authentication import ApiTokenAuthentication
from .authorization import VizAuthorization


class VizResource( Resource ):

    class Meta:
        resource_name = 'viz'

        detail_allowed_methods = [ 'get', 'post' ]

        # Ensure we have an API token before returning any data.
        # TODO: Make sure this API token concept works with public/private
        # data.
        authentication = MultiAuthentication( ApiTokenAuthentication(),
                                              SessionAuthentication() )

        authorization = VizAuthorization()

    def dehydrate( self, bundle ):
        serializer = VisualizationSerializer()
        bundle.data = serializer.serialize( [bundle.obj] )
        return bundle

    def get_detail( self, request, **kwargs ):

        # Grab the survey that we're querying survey data for
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
            new_id = new_viz.save()
            response_data = { 'success': True, 'id': str( new_id ) }
            return self.create_response( request, response_data )

        except ValueError as e:
            return HttpBadRequest( str( e ) )
