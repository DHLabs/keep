from django.conf.urls import patterns, url

urlpatterns = patterns('',

    url( r'^$', 'backend.views.home', name='home' ),

    # User dashboard
    url( r'^dashboard', 'backend.views.dashboard', name='dashboard' ),

    # User settings
    url( r'^settings', 'backend.views.settings', name='settings' ),

)
