# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_auto_20150612_1518'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='singlespaceuserequest',
            name='setup_cleanup_time',
        ),
        migrations.AddField(
            model_name='singlespaceuserequest',
            name='cleanup_time',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='singlespaceuserequest',
            name='setup_time',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
