from django.conf.urls import patterns, url

## Webform/Data submission ##
urlpatterns = patterns( 'repos.views',

    # Create new data repository
    url( r'^repo/new/$', 'new_repo',
         name='repo_new' ),

    # Delete form
    url( r'^repo/delete/(?P<form_id>\w+)/$', 'delete_form',
         name='form_delete'),

    # Toggle form publicness
    url( r'^repo/share/(?P<form_id>\w+)/$', 'toggle_public',
         name='form_toggle_public' ),

    # Web form
    url( r'^repo/webform/(?P<form_id>\w+)/$', 'webform',
         name='form_webform' ),

    url( r'^repo/viz/map_visualize/$', 'map_visualize',
         name='map_visualize' ),

    # View data repository
    url( r'^(?P<username>\w+)/(?P<form_id>\w+)/$', 'visualize',
         name='form_visualize' ),

)
