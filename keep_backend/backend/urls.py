from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import TemplateView

from api.data import DataResource
from api.filters import FilterSetResource
from api.repo import RepoResource
from api.study import StudyResource
from api.user import UserResource
from api.viz import VizResource
from api.vocab import VocabResource

# Register resources to make API available
from tastypie.api import Api
v1_api = Api( api_name='v1' )

v1_api.register( DataResource() )
v1_api.register( FilterSetResource() )
v1_api.register( RepoResource() )
v1_api.register( StudyResource() )
v1_api.register( UserResource() )
v1_api.register( VizResource() )
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
    url( regex=r'^(?P<username>(?!static|media)\w+)/$',
    	 view='user_dashboard',
    	 name='user_dashboard' ),

)

# Static pages
urlpatterns += url(r'^features',
    TemplateView.as_view(template_name='features.html'),
    name='features'),


if settings.DEBUG:
    admin.autodiscover()
    urlpatterns += patterns( '',
                             ( r'^keep-admin/', include( admin.site.urls )),
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
    urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )
