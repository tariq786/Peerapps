from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^unsubscribe/$', "peerblog.views.unsubscribe"),
    url(r'^subscribe/$', "peerblog.views.subscribe"),
    url(r'^view_latest_post/$', "peerblog.views.view_latest_post"),
    url(r'^get_blogs/$', "peerblog.views.get_blogs"),
    url(r'^scan_blogs/$', "peerblog.views.scan_blogs"),
    url(r'^submit_blogpost/$', "peerblog.views.submit_blogpost"),
)