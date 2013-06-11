from django.conf.urls import patterns, url

## Webform/Data submission ##
urlpatterns = patterns( 'organizations.views',

    url( regex=r'^organizations/new/$',
         view='organization_new',
         name='organization_new' ),

    url( regex=r'^organizations/(?P<org>\w+)/delete/$',
         view='organization_delete',
         name='organization_delete' ),

    url( regex=r'^organizations/(?P<org>\w+)/$',
         view='organization_dashboard',
         name='organization_dashboard' ),

    url( regex=r'^organizations/(?P<org>\w+)/repo/new/$',
         view='organization_repo_new',
         name='organization_repo_new' ),

    url( regex=r'^organizations/(?P<org>\w+)/member/add/(?P<user>\w+)/$',
         view='organization_member_add',
         name='organization_member_add' ),

    url( regex=r'^organizations/(?P<org>\w+)/member/accept/(?P<user>\w+)/$',
         view='organization_member_accept',
         name='organization_member_accept' ),

    url( regex=r'^organizations/(?P<org>\w+)/member/ignore/(?P<user>\w+)/$',
         view='organization_member_ignore',
         name='organization_member_ignore' ),
)
