from django.conf.urls import patterns, url

## Webform/Data submission ##
urlpatterns = patterns( 'backend.surveys.views',

    # Delete form
    url( r'^forms/delete/(?P<form_id>\w+)',
         'delete_form',
         name='delete_form'),

    # Toggle form publicness
    url( r'^forms/share/(?P<form_id>\w+)',
         'toggle_public',
         name='toggle_public' ),

    # Web form
    url( r'^webform/(?P<form_id>\w+)', 'webform',
         name='webform' ),

    # Data Visualization
    url( r'^visualize/(?P<form_id>\w+)', 'visualize',
         name='visualize' ),

    url( r'^map_visualize/', 'map_visualize',
         name='map_visualize' ),

)
