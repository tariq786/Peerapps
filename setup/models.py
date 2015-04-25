from django.db import models

class BlockchainScan(models.Model):
    last_index = models.IntegerField(default=0, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.last_index)

    class Meta:
        verbose_name = 'BlockchainScan'
        verbose_name_plural = 'BlockchainScan'
        app_label = "setup"

class MemPoolScan(models.Model):
    txids_scanned = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.id)

    class Meta:
        verbose_name = 'MemPoolScan'
        verbose_name_plural = 'MemPoolScan'
        app_label = "setup"
