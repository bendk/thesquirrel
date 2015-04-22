# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20150417_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='bottomliner',
            field=models.CharField(default='unset', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.CharField(default='unset', max_length=255),
            preserve_default=False,
        ),
    ]
