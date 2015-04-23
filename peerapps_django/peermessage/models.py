from django.db import models

class GPGKey(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    address = models.CharField(max_length=255)
    tag = models.CharField(max_length=255)
    block_index = models.CharField(max_length=255)
    tx_id = models.CharField(max_length=255)
    mine = models.BooleanField(default=False)

    time = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.key)

    class Meta:
        verbose_name = 'GPGKey'
        verbose_name_plural = 'GPGKeys'
        app_label = "peermessage"

class Spamlist(models.Model):
    address = models.CharField(max_length=255, primary_key=True)
    time = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.address)

    class Meta:
        verbose_name = 'Spamlist'
        verbose_name_plural = 'Spamlist'
        app_label = "peermessage"

class Message(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    address_from = models.CharField(max_length=255)
    address_to = models.CharField(max_length=255)
    block_index = models.CharField(max_length=255)
    tx_id = models.CharField(max_length=255)
    msg = models.TextField(blank=True, null=True)

    time = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.key)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        app_label = "peermessage"
