from django.conf.urls import patterns, url

urlpatterns = patterns('',

    url( r'^$', 'backend.views.home', name='home' ),

    ## User urls ##

    # User dashboard
    url( r'^dashboard', 'backend.views.dashboard', name='dashboard' ),

    # User settings
    url( r'^settings', 'backend.views.settings', name='settings' ),

    ## Webform/Data submission ##

    url( r'^webform/(?P<form_id>\w+)',
         'backend.views.webform', name='webform' ),


    ## Data Visualization ##
    url( r'^visualize/(?P<form_id>\w+)', 'backend.views.visualize',
         name='visualize' ),

    #url( r'^insert_data/', 'backend.views.insert_data' ),
)
