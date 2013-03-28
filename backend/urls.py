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

# Webform/Data submission ##
urlpatterns += patterns( 'backend.views',

    # Delete form
    url( r'^forms/delete/(?P<form_id>\w+)', 'delete_form',
         name='delete_form'),

    # Web form
    url( r'^webform/(?P<form_id>\w+)', 'webform',
         name='webform' ),

    # Data Visualization
    url( r'^visualize/(?P<form_id>\w+)', 'visualize',
         name='visualize' ),

    url( r'^map_visualize/', 'map_visualize',
         name='map_visualize' ),

)
