'''
    openrosa.urls.py

    Contains URL which map from the fantastic and sensible ODKCollect/OpenROSA
    API to our RESTful API. Since redirects only work for GET requests, any
    POSTs by the ODKCollect API are directly passed to the corresponding
    function to be handled.

    @author Andrew Huynh
'''
from django.conf.urls import patterns, url

urlpatterns = patterns( 'openrosa.views',

    # Return a list of forms uploaded/shared to the specified user
    url( r'^bs/(?P<username>\w+)/formList$', 'formlist' ),

    # Parse an XML submission file and add the data into the specified repo.
    url( r'^bs/(?P<username>\w+)/submission', 'xml_submission'),
)
