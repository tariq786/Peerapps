# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GPGKey',
            fields=[
                ('key', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('address', models.CharField(max_length=255)),
                ('tag', models.CharField(max_length=255)),
                ('block_index', models.CharField(max_length=255)),
                ('tx_id', models.CharField(max_length=255)),
                ('mine', models.BooleanField(default=False)),
                ('time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': 'GPGKey',
                'verbose_name_plural': 'GPGKeys',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('key', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('address_from', models.CharField(max_length=255)),
                ('address_to', models.CharField(max_length=255)),
                ('block_index', models.CharField(max_length=255)),
                ('tx_id', models.CharField(max_length=255)),
                ('msg', models.TextField(null=True, blank=True)),
                ('time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
        ),
        migrations.CreateModel(
            name='Spamlist',
            fields=[
                ('address', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': 'Spamlist',
                'verbose_name_plural': 'Spamlist',
            },
        ),
    ]
