# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_spaceusenote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spaceuserequest',
            name='email',
            field=models.EmailField(max_length=255, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='spaceuserequest',
            name='name',
            field=models.CharField(max_length=255, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='spaceuserequest',
            name='state',
            field=models.CharField(default=b'P', max_length=1, choices=[(b'P', 'Pending'), (b'A', 'Approved'), (b'B', 'Approved (Pending deposit)'), (b'D', 'Declined')]),
            preserve_default=True,
        ),
    ]
