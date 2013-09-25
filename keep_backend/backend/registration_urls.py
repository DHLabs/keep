"""
URLConf for Django user registration and authentication.

Recommended usage is a call to ``include()`` in your project's root
URLConf to include this URLConf for any URL beginning with
``/accounts/``.

"""

from django.conf.urls import patterns, url
from django.shortcuts import render
from django.contrib.auth import views as auth_views

from twofactor.auth_forms import TwoFactorAuthenticationForm
from registration.views import activate

from backend.views import register

# Generate/Delete API Keys URLs
urlpatterns = patterns( 'backend.views',
    url( r'^generate_key', 'generate_api_key', name='generate_api_key' ),
    url( r'^delete_key/(?P<key>\w+)', 'delete_api_key',
         name='delete_api_key' ), )


# Registration/Login URLs
urlpatterns += patterns('',

    url(r'^activate/(?P<activation_key>\w+)/$',
        activate,
        { 'backend': 'registration.backends.default.DefaultBackend' },
        name='registration_activate'),

    url(r'^registration_complete',
        'backend.views.registration_complete',
        name='registration_activation_complete'),


    url( r'^resend_activation/', 'backend.views.resend_activation',
         name='resend_activation' ),

    url(r'^login/$',
        auth_views.login,
        { 'template_name': 'registration/login.html',
        'authentication_form': TwoFactorAuthenticationForm},
        name='auth_login'),

    url(r'^logout/$',
        auth_views.logout,
        kwargs={ 'next_page': '/' },
        name='auth_logout'),

    url(r'^password/change/$',
        auth_views.password_change,
        name='auth_password_change'),

    url(r'^password/change/done/$',
        auth_views.password_change_done,
        name='auth_password_change_done'),

    url(r'^password/reset/$',
        auth_views.password_reset,
        name='auth_password_reset'),

    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        name='auth_password_reset_confirm'),

    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        name='auth_password_reset_complete'),

    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        name='auth_password_reset_done'),

    url(r'^register/$',
        register,
        name='registration_register'),

    url(r'^register/complete/$',
        render,
        {'template': 'registration/registration_complete.html'},
        name='registration_complete'), )
