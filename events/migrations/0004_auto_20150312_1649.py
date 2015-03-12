# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_ongoingspaceuserequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ongoingspaceuserequest',
            name='email',
            field=models.EmailField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='spaceuserequest',
            name='email',
            field=models.EmailField(max_length=255),
            preserve_default=True,
        ),
    ]
