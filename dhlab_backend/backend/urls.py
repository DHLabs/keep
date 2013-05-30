from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from backend.api import RepoResource, DataResource, UserResource

# Register resources to make API available
from tastypie.api import Api
v1_api = Api( api_name='v1' )
v1_api.register( RepoResource() )
v1_api.register( DataResource() )
v1_api.register( UserResource() )

# User views URLs
urlpatterns = patterns( 'backend.views',

    # Basic index page
    url( r'^$', 'home', name='home' ),

    # Create new data repository
    url( r'^report/new/$', 'build_report', name='report_build' ),

    # User settings
    url( r'^settings/$', 'settings', name='settings' ),

    # User dashboard
    url( r'^(?P<username>\w+)/$', 'user_dashboard', name='user_dashboard' ),

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
    urlpatterns += static('/css/', document_root='static/css/')
    urlpatterns += static('/img/', document_root='static/img/')
    urlpatterns += static('/js/', document_root='static/js/')
