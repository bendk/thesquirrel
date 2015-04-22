# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_auto_20150422_1457'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventRepeatExclude',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('event', models.ForeignKey(related_name='excludes', to='events.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='eventrepeat',
            name='type',
            field=models.CharField(max_length=3, choices=[(b'W', b'Every week'), (b'2W', b'Every other week'), (b'1M', b'First week of the month'), (b'2M', b'Second week of the month'), (b'3M', b'Third week of the month'), (b'4M', b'Fourth week of the month'), (b'LM', b'Last week of the month'), (b'13M', b'1st/3rd week of the month'), (b'24M', b'2nd/4th week of the month')]),
            preserve_default=True,
        ),
    ]
