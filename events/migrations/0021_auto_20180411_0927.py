# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0020_auto_20180410_2033'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE events_spaceuserequest SET state = 'P' WHERE state = 'B'",
        )
    ]
