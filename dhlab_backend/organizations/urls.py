from django.conf.urls import patterns, url

## Webform/Data submission ##
urlpatterns = patterns( 'organizations.views',

    url( regex=r'^organizations/new/$',
         view='organization_new',
         name='organization_new' ),

    url( regex=r'^organizations/(?P<org>\w+)/$',
         view='organization_dashboard',
         name='organization_dashboard' ),

    url( regex=r'^organizations/(?P<org>\w+)/repo/new/$',
         view='organization_repo_new',
         name='organization_repo_new' ),

)
