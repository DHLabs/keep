import settings

from django.conf.urls.defaults import patterns, include, url

# Turn on Django Admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns( '',

    # Landing page / standard copy pages
    url(r'', include( 'backend.urls' ) ),

    # Account registration / login
    url(r'^accounts/', include( 'backend.registration_urls' ) ),

    # Django Admin pages
    url(r'^admin/', include(admin.site.urls)),

    # static media
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)
