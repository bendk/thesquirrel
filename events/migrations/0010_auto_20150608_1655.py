# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_event_space_request'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spaceuserequest',
            name='state',
            field=models.CharField(default=b'P', max_length=1, choices=[(b'P', 'Pending'), (b'A', 'Approved'), (b'B', 'Approved Pending Deposit'), (b'D', 'Declined'), (b'C', 'Canceled')]),
            preserve_default=True,
        ),
    ]
