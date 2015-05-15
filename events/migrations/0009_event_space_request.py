# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_auto_20150512_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='space_request',
            field=models.ForeignKey(to='events.SpaceUseRequest', null=True),
            preserve_default=True,
        ),
    ]
