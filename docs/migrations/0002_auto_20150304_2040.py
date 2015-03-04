# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import editor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='body',
            field=editor.fields.EditorTextField(),
            preserve_default=True,
        ),
    ]
