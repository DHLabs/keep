from django.conf.urls import patterns, url

## Webform/Data submission ##
urlpatterns = patterns( 'repos.views',

    # Create new data repository
    url(regex=r'^repo/new/$',
        view='new_repo',
        name='repo_new'),

    # Delete form
    url(regex=r'^repo/delete/(?P<repo_id>\w+)/$',
        view='delete_repo',
        name='repo_delete'),

    # Toggle form publicness
    url(regex=r'^repo/share/(?P<repo_id>\w+)/$',
        view='toggle_public',
        name='repo_toggle_public' ),

    # View data repository
    url(regex=r'^(?P<username>\w+)/(?P<repo_name>\w+)/$',
        view='repo_viz',
        name='repo_visualize' ),

    # Web form
    url(regex=r'^(?P<username>\w+)/(?P<repo_name>\w+)/webform/$',
        view='webform',
        name='repo_webform' ),

)
