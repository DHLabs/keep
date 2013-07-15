from django.conf.urls import include, patterns, url

from vocab.api import VocabResource

from tastypie.api import Api

v1_api = Api( api_name='v1' )
v1_api.register( VocabResource() )

# API urls
urlpatterns = patterns( '', url(r'^api/', include( v1_api.urls ) ) )