# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlockchainScan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_index', models.IntegerField(default=0, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'BlockchainScan',
                'verbose_name_plural': 'BlockchainScan',
            },
        ),
        migrations.CreateModel(
            name='MemPoolScan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('txids_scanned', models.TextField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'MemPoolScan',
                'verbose_name_plural': 'MemPoolScan',
            },
        ),
    ]
