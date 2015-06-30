# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import connection, models, migrations
import datetime

def set_event_repeat_fields(apps, schema_editor):
    cursor = connection.cursor()
    cursor.execute("UPDATE events_eventrepeat SET start_date=("
                   "SELECT date + INTERVAL 1 DAY "
                   "FROM events_event "
                   "WHERE events_event.id = events_eventrepeat.event_id)")
    cursor.execute("UPDATE events_eventrepeat SET start_time=("
                   "SELECT start_time "
                   "FROM events_event "
                   "WHERE events_event.id = events_eventrepeat.event_id)")
    cursor.execute("UPDATE events_eventrepeat SET end_time=("
                   "SELECT end_time "
                   "FROM events_event "
                   "WHERE events_event.id = events_eventrepeat.event_id)")

def reverse_set_event_repeat_fields(apps, schema_editor):
    # nothing to do here, the columns are going to be deleted in the reverse
    # migration
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0014_auto_20150626_1517'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventrepeat',
            old_name='until',
            new_name='end_date',
        ),
        migrations.AddField(
            model_name='eventrepeat',
            name='start_time',
            field=models.TimeField(default=datetime.time(0, 0)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventrepeat',
            name='end_time',
            field=models.TimeField(default=datetime.time(0, 0)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventrepeat',
            name='start_date',
            field=models.DateField(default=datetime.date(2015, 1, 1)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calendaritem',
            name='event',
            field=models.ForeignKey(related_name='calendar_items', to='events.Event'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventrepeat',
            name='event',
            field=models.ForeignKey(related_name='repeat_set', to='events.Event'),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='event',
            name='author',
        ),
        migrations.RunPython(set_event_repeat_fields,
                             reverse_set_event_repeat_fields)
    ]
