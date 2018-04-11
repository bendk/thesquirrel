# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0019_auto_20171006_1309'),
    ]

    operations = [
        migrations.AddField(
            model_name='spaceuserequest',
            name='deposit_paid',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='spaceuserequest',
            name='has_bottomliner',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
