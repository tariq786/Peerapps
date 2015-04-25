from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^peermessage/', include('peermessage.urls')),
    url(r'^peermarket/', include('peermarket.urls')),
    url(r'^peerblog/', include('peerblog.urls')),
    url(r'^peercoin_minting/', include('minting.urls')),
    url(r'^', include('setup.urls')),

    url(r'^admin/', include(admin.site.urls)),
]
