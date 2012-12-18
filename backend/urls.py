from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    url( r'^$', 'backend.views.home', name='home' ),

    # User dashboard
    url( r'^dashboard', 'backend.views.dashboard', name='dashboard' ),

    # User settings
    url( r'^settings', 'backend.views.settings', name='settings' ),

)
