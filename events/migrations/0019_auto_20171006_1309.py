# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0018_auto_20160319_2002'),
    ]

    operations = [
        migrations.AddField(
            model_name='singlespaceuserequest',
            name='number_of_people',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='singlespaceuserequest',
            name='space_needs',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
