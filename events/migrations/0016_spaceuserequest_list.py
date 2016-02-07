# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_auto_20150628_2053'),
    ]

    operations = [
        migrations.AddField(
            model_name='spaceuserequest',
            name='list',
            field=models.CharField(default=b'I', max_length=1, choices=[(b'I', b'Inbox'), (b'W', b'Waiting for them'), (b'M', b'Waiting for meeting'), (b'B', b'Waiting for bottomliner'), (b'C', b'Complete')]),
            preserve_default=True,
        ),
    ]
