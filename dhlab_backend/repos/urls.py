from django.conf.urls import patterns, url

## Webform/Data submission ##
urlpatterns = patterns( 'repos.views',

    # Batch create a repo and import data into it from a 
    # CSV file.
    url(regex=r'^repo/batch/$',
        view='batch_repo',
        name='repo_batch' ),

    # Create new data repository
    url(regex=r'^repo/new/$',
        view='new_repo',
        name='repo_new'),

    # Edit form
    url(regex=r'^repo/edit/(?P<repo_id>[-\w]+)/$',
        view='edit_repo',
        name='repo_edit'),

    # Delete form
    url(regex=r'^repo/delete/(?P<repo_id>[-\w]+)/$',
        view='delete_repo',
        name='repo_delete'),

    # Toggle form publicness
    url(regex=r'^repo/share/(?P<repo_id>[-\w]+)/$',
        view='toggle_public',
        name='repo_toggle_public' ),

    # View data repository
    url(regex=r'^(?P<username>[-\w]+)/(?P<repo_name>[-\w]+)/$',
        view='repo_viz',
        name='repo_visualize' ),

    # Web form
    url(regex=r'^(?P<username>[-\w]+)/(?P<repo_name>[-\w]+)/webform/$',
        view='webform',
        name='repo_webform' ),

)
