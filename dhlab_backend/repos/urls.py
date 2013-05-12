from django.conf.urls import patterns, url

## Webform/Data submission ##
urlpatterns = patterns( 'repos.views',

    # Create new data repository
    url( r'^repo/new/$', 'new_repo',
         name='repo_new' ),

    # Delete form
    url( r'^repo/delete/(?P<repo_id>\w+)/$', 'delete_repo',
         name='repo_delete'),

    # Toggle form publicness
    url( r'^repo/share/(?P<repo_id>\w+)/$', 'toggle_public',
         name='repo_toggle_public' ),

    url( r'^repo/viz/map_visualize/$', 'map_visualize',
         name='map_visualize' ),

    # View data repository
    url( r'^(?P<username>\w+)/(?P<repo_name>\w+)/$', 'repo_viz',
         name='repo_visualize' ),

    # Web form
    url( r'^(?P<username>\w+)/(?P<repo_name>\w+)/webform/$', 'webform',
         name='repo_webform' ),

)
