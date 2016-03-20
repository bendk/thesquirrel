# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0017_auto_20160207_0815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spaceuserequest',
            name='list',
            field=models.CharField(default=b'I', max_length=1, choices=[(b'I', b'Inbox'), (b'W', b'Waiting for them'), (b'N', b'Needs discussion'), (b'M', b'Coming to meeting'), (b'B', b'Needs bottomliner'), (b'C', b'Complete')]),
            preserve_default=True,
        ),
    ]
