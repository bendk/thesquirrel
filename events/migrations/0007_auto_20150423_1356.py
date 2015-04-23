# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_auto_20150422_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventrepeatexclude',
            name='date',
            field=models.DateField(unique=True),
            preserve_default=True,
        ),
    ]
