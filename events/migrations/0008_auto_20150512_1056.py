# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_auto_20150423_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spaceuserequest',
            name='phone_number',
            field=models.CharField(max_length=255, db_index=True),
            preserve_default=True,
        ),
    ]
