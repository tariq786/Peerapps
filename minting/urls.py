from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^peercoin_minting_data/$', "minting.views.peercoin_minting_data"),
)