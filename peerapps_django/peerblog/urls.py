from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^unsubscribe/$', "views.unsubscribe"),
    url(r'^subscribe/$', "views.subscribe"),
    url(r'^view_latest_post/$', "views.view_latest_post"),
    url(r'^get_blogs/$', "views.get_blogs"),
    url(r'^scan_blogs/$', "views.scan_blogs"),
    url(r'^submit_blogpost/$', "views.submit_blogpost"),
    url(r'^peerblog/$', "views.peerblog")
)