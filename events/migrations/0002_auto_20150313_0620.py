# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpaceUseRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('state', models.CharField(default=b'P', max_length=1, choices=[(b'P', 'Pending'), (b'A', 'Approved'), (b'D', 'Denied')])),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('squirrel_member', models.CharField(max_length=255, blank=True)),
                ('organization', models.CharField(max_length=255, blank=True)),
                ('website', models.CharField(max_length=255, blank=True)),
                ('mission', models.TextField(blank=True)),
                ('phone_number', models.CharField(max_length=255)),
                ('additional_comments', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SingleSpaceUseRequest',
            fields=[
                ('spaceuserequest_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='events.SpaceUseRequest')),
                ('event_type', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('setup_cleanup_time', models.CharField(max_length=255, blank=True)),
                ('event_charge', models.CharField(max_length=255)),
                ('squirrel_donation', models.TextField(blank=True)),
            ],
            options={
            },
            bases=('events.spaceuserequest',),
        ),
        migrations.CreateModel(
            name='OngoingSpaceUseRequest',
            fields=[
                ('spaceuserequest_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='events.SpaceUseRequest')),
                ('dates', models.CharField(max_length=255)),
                ('frequency', models.CharField(max_length=255)),
                ('squirrel_goals', models.TextField()),
                ('space_needs', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=('events.spaceuserequest',),
        ),
        migrations.AlterIndexTogether(
            name='spaceuserequest',
            index_together=set([('state', 'changed')]),
        ),
    ]