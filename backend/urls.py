from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    url( r'^$', 'backend.views.home', name='home' ),

    url( r'^dashboard', 'backend.views.dashboard', name='dashboard' ),

)
