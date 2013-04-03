from django.conf.urls import patterns, url

## Webform/Data submission ##
urlpatterns = patterns( 'surveys.views',

    # Create new data repository
    url( r'^repo/new/$', 'new_repo', name='repo_new' ),

    # Delete form
    url( r'^forms/delete/(?P<form_id>\w+)/$',
         'delete_form',
         name='form_delete'),

    # Toggle form publicness
    url( r'^forms/share/(?P<form_id>\w+)/$',
         'toggle_public',
         name='form_toggle_public' ),

    # Web form
    url( r'^forms/webform/(?P<form_id>\w+)/$', 'webform',
         name='form_webform' ),

    # Data Visualization
    url( r'^(?P<username>\w+)/(?P<form_id>\w+)/$', 'visualize',
         name='form_visualize' ),

    url( r'^forms/viz/map_visualize/$', 'map_visualize',
         name='map_visualize' ),

)
