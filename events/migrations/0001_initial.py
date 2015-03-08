# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import editor.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('body', editor.fields.EditorTextField()),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(db_index=True)),
                ('event', models.ForeignKey(related_name='date_set', to='events.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventRepeat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=3, choices=[(b'W', b'Every Week'), (b'2W', b'Every Other Week'), (b'1M', b'First Week of the month'), (b'2M', b'Second Week of the month'), (b'3M', b'Third Week of the month'), (b'4M', b'Fourth Week of the month'), (b'LM', b'Last Week of the month'), (b'13M', b'1st/3rd Week of the month'), (b'24M', b'2nd/4th Week of the month')])),
                ('until', models.DateField()),
                ('su', models.BooleanField(default=False)),
                ('mo', models.BooleanField(default=False)),
                ('tu', models.BooleanField(default=False)),
                ('we', models.BooleanField(default=False)),
                ('th', models.BooleanField(default=False)),
                ('fr', models.BooleanField(default=False)),
                ('sa', models.BooleanField(default=False)),
                ('event', models.OneToOneField(related_name='repeat', to='events.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
