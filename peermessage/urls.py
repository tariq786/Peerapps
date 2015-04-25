from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^autocomplete_address/$', "peermessage.views.autocomplete_address"),
    url(r'^delete_message/$', "peermessage.views.delete_message"),
    url(r'^remove_from_spamlist/$', "peermessage.views.remove_from_spamlist"),
    url(r'^mark_address_as_spam/$', "peermessage.views.mark_address_as_spam"),
    url(r'^get_spamlist/$', "peermessage.views.get_spamlist"),
    url(r'^get_messages/$', "peermessage.views.get_messages"),
    url(r'^transmit_message/$', "peermessage.views.transmit_message"),
    url(r'^publish_pk/$', "peermessage.views.publish_pk"),
    url(r'^setup_gpg/$', "peermessage.views.setup_gpg"),
    url(r'^check_setup_status/$', "peermessage.views.check_setup_status"),
    url(r'^get_addresses/$', "peermessage.views.get_addresses"),
    url(r'^peermessage/$', "peermessage.views.peermessage"),
    url(r'^spamlist/$', "peermessage.views.spamlist"),
    url(r'^$', "peermessage.views.peermessage"),
)