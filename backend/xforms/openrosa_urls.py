'''
    backend.xforms.openrosa_urls.py

    Contains URL which map from the fantastic and sensible ODKCollect/OpenROSA
    API to our RESTful API. Since redirects only work for GET requests, any
    POSTs by the ODKCollect API are directly passed to the corresponding
    function to be handled.

    @author Andrew Huynh
'''
from django.conf.urls import url

openrosa_urls = [

    # Return a list of forms uploaded/shared to the specified user
    url( r'^bs/(?P<username>\w+)/formList$',
            'backend.xforms.formlist' ),

    url( r'^bs/(?P<username>\w+)/submission', 'backend.views.xml_submission'),

    # Returns a list of submissions for a specified form & user
    url( r'^bs/(?P<username>\w+)/forms/(?P<form_id>[^/]+)/submission/(?P<sub_id>[^/]+)$',
            'backend.xforms.submission_detail' ),
]

# # odk data urls
# url(r"^submission$", 'odk_logger.views.submission'),
# url(r"^(?P<username>\w+)/formList$", 'odk_logger.views.formList'),
# url(r"^(?P<username>\w+)/xformsManifest/(?P<id_string>[^/]+)$",
#     'odk_logger.views.xformsManifest'),
# url(r"^(?P<username>\w+)/submission$", 'odk_logger.views.submission'),
# url(r"^(?P<username>\w+)/bulk-submission$", 'odk_logger.views.bulksubmission'),
# url(r"^(?P<username>\w+)/bulk-submission-form$", 'odk_logger.views.bulksubmission_form'),
# url(r"^(?P<username>\w+)/forms/(?P<id_string>[^/]+)/form\.xml$", 'odk_logger.views.download_xform', name="download_xform"),
# url(r"^(?P<username>\w+)/forms/(?P<id_string>[^/]+)/form\.xls$", 'odk_logger.views.download_xlsform', name="download_xlsform"),
# url(r"^(?P<username>\w+)/forms/(?P<id_string>[^/]+)/form\.json", 'odk_logger.views.download_jsonform', name="download_jsonform"),
# url(r"^(?P<username>\w+)/delete/(?P<id_string>[^/]+)/$", 'odk_logger.views.delete_xform'),
# url(r"^(?P<username>\w+)/(?P<id_string>[^/]+)/toggle_downloadable/$", 'odk_logger.views.toggle_downloadable'),

