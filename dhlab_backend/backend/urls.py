from django.conf.urls import patterns, url

# User views URLs
urlpatterns = patterns( 'backend.views',

    # Basic index page
    url( r'^$', 'home', name='home' ),

    # User dashboard
    url( r'^dashboard', 'dashboard', name='dashboard' ),

    # User settings
    url( r'^settings', 'settings', name='settings' ),
)