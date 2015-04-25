from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^config_automatic_setup$', "setup.views.config_automatic_setup"),
    url(r'^check_peercoin_conf/$', "setup.views.check_peercoin_conf"),
    url(r'^$', "setup.views.setup"),
)