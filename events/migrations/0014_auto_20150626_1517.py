# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_auto_20150626_0715'),
    ]

    operations = [
        migrations.RenameModel('eventdate', 'calendaritem'),
    ]
