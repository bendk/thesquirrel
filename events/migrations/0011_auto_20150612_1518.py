# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_auto_20150608_1655'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='spaceusenote',
            options={'ordering': ['datetime']},
        ),
    ]
