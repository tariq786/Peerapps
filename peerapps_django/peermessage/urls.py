from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^autocomplete_address/$', "views.autocomplete_address"),
    url(r'^delete_message/$', "views.delete_message"),
    url(r'^remove_from_spamlist/$', "views.remove_from_spamlist"),
    url(r'^mark_address_as_spam/$', "views.mark_address_as_spam"),
    url(r'^get_spamlist/$', "views.get_spamlist"),
    url(r'^get_messages/$', "views.get_messages"),
    url(r'^transmit_message/$', "views.transmit_message"),
    url(r'^publish_pk/$', "views.publish_pk"),
    url(r'^setup_gpg/$', "views.setup_gpg"),
    url(r'^check_setup_status/$', "views.check_setup_status"),
    url(r'^get_addresses/$', "views.get_addresses"),
    url(r'^peermessage/$', "views.peermessage"),
    url(r'^spamlist/$', "views.spamlist"),
)