from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from api.resources import RepoResource, DataResource, UserResource
from vocab.api import VocabResource

# Register resources to make API available
from tastypie.api import Api
v1_api = Api( api_name='v1' )
v1_api.register( RepoResource() )
v1_api.register( DataResource() )
v1_api.register( UserResource() )
v1_api.register( VocabResource() )

# User views URLs
urlpatterns = patterns( 'backend.views',

    # Basic index page
    url( regex=r'^$',
    	 view='home',
    	 name='home' ),

    # User settings
    url( regex=r'^settings/$',
    	 view='settings',
    	 name='settings' ),

    # User dashboard
    url( regex=r'^(?P<username>\w+)/$',
    	 view='user_dashboard',
    	 name='user_dashboard' ),

)

# Add API urls
urlpatterns += patterns( '', url(r'^api/', include( v1_api.urls ) ) )

# Account registration / login
urlpatterns += patterns( '', url( r'^accounts/',
                                  include( 'backend.registration_urls' ) ) )

urlpatterns += patterns( '', url( r'', include( 'organizations.urls' ) ) )

urlpatterns += patterns( '', url( r'', include( 'repos.urls' ) ) )

# Handle the ODKCollect APIs
urlpatterns += patterns( '', url( r'', include( 'openrosa.urls' ) ) )

# Handle static files on local dev machine
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
