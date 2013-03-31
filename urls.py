from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Turn on Django Admin
from django.contrib import admin
admin.autodiscover()

from backend.api import FormResource, DataResource
from backend.xforms.urls import openrosa_urls

# Register resources to make API available
from tastypie.api import Api
v1_api = Api( api_name='v1' )
v1_api.register( FormResource() )
v1_api.register( DataResource() )

urlpatterns = patterns( '',

    # Landing page / standard copy pages
    url(r'', include( 'backend.urls' ) ),

    # Form related actions
    url(r'', include( 'backend.surveys.urls' ) ),

    # Account registration / login
    url(r'^accounts/', include( 'backend.registration_urls' ) ),

    # Django Admin pages
    url(r'^admin/', include(admin.site.urls)),

    # DHLab REST API
    url(r'^api/', include( v1_api.urls ) ),
)

# Handle the ODKCollect APIs
urlpatterns += openrosa_urls

# Handle static files
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
