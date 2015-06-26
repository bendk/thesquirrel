# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import connection, models, migrations
import datetime

def set_event_date_times(apps, schema_editor):
    cursor = connection.cursor()
    cursor.execute("UPDATE events_eventdate SET start_time=("
                   "SELECT start_time "
                   "FROM events_event "
                   "WHERE events_event.id = events_eventdate.event_id)")
    cursor.execute("UPDATE events_eventdate SET end_time=("
                   "SELECT end_time "
                   "FROM events_event "
                   "WHERE events_event.id = events_eventdate.event_id)")

def reverse_set_event_date_times(apps, schema_editor):
    # nothing to do here, the columns are going to be deleted in the reverse
    # migration
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_auto_20150623_0754'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventdate',
            name='end_time',
            field=models.TimeField(default=datetime.time(0, 0)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventdate',
            name='start_time',
            field=models.TimeField(default=datetime.time(0, 0)),
            preserve_default=False,
        ),
        migrations.RunPython(set_event_date_times,
                             reverse_set_event_date_times)
    ]
