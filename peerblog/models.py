from django.db import models

class Subscription(models.Model):
    address = models.CharField(max_length=255, primary_key=True)
    time = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.address)

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        app_label = "peerblog"

class Blog(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    address_from = models.CharField(max_length=255)
    block_index = models.CharField(max_length=255)
    tx_id = models.CharField(max_length=255)
    msg = models.TextField(blank=True, null=True)

    time = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.key)

    class Meta:
        verbose_name = 'Blog'
        verbose_name_plural = 'Blogs'
        app_label = "peerblog"
