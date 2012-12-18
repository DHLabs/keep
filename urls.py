import settings

from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static import static

# Turn on Django Admin
from django.contrib import admin
admin.autodiscover()

from twofactor.api_auth import UserResource

from tastypie.api import Api
v1_api = Api( api_name='v1' )
v1_api.register( UserResource() )

urlpatterns = patterns( '',

    # Landing page / standard copy pages
    url(r'', include( 'backend.urls' ) ),

    # Account registration / login
    url(r'^accounts/', include( 'backend.registration_urls' ) ),

    # Django Admin pages
    url(r'^admin/', include(admin.site.urls)),

    # DHLab REST API
    url(r'^api/', include( v1_api.urls ) ),

)

# Handle uploaded files
urlpatterns += static(  r'^media/<?P<path>.*)$',
                        document_root=settings.MEDIA_ROOT )

# Handle static files
urlpatterns += static(  r'^static/<?P<path>.*)$',
                        document_root=settings.STATIC_ROOT )
