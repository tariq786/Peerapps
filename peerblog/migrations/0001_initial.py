# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('key', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('address_from', models.CharField(max_length=255)),
                ('block_index', models.CharField(max_length=255)),
                ('tx_id', models.CharField(max_length=255)),
                ('msg', models.TextField(null=True, blank=True)),
                ('time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': 'Blog',
                'verbose_name_plural': 'Blogs',
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('address', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': 'Subscription',
                'verbose_name_plural': 'Subscriptions',
            },
        ),
    ]
