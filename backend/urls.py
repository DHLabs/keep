from django.conf.urls import patterns, url

urlpatterns = patterns('',

    url( r'^$', 'backend.views.home', name='home' ),

    ## User urls ##

    # User dashboard
    url( r'^dashboard', 'backend.views.dashboard', name='dashboard' ),

    # User settings
    url( r'^settings', 'backend.views.settings', name='settings' ),

    ## Webform/Data submission ##

    url( r'^submission', 'backend.views.submission', name='submission' ),

    url( r'^webform/(?P<form_id>\w+)',
         'backend.views.webform', name='webform' ),
)
