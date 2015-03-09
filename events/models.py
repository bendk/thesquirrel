# thesquirrel.org
#
# Copyright (C) 2015 Flying Squirrel Community Space
#
# thesquirrel.org is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# thesquirrel.org is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with thesquirrel.org.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from dateutil import rrule

from editor.fields import EditorTextField
from . import repeat
from .utils import format_time

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = EditorTextField()
    created = models.DateTimeField(default=timezone.now)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    author = models.ForeignKey(User)

    def __unicode__(self):
        return u'Event: {}'.format(self.title)

    def update_dates(self):
        self.date_set.all().delete()
        dates = set([self.date])
        if self.has_repeat():
            dates.update(dt.date() for dt in self.repeat.calc_repeat_rrule())
        EventDate.objects.bulk_create([
            EventDate(event=self, date=date)
            for date in dates
        ])

    def get_start_time_display(self):
        return format_time(self.start_time)

    def get_end_time_display(self):
        return format_time(self.end_time)

    def has_repeat(self):
        try:
            self.repeat
        except EventRepeat.DoesNotExist:
            return False
        else:
            return True

# list of (field_name, rrule_class, display_string) tuples
weekday_field_info = [
    ('mo', rrule.MO, _('Monday')),
    ('tu', rrule.TU, _('Tuesday')),
    ('we', rrule.WE, _('Wednesday')),
    ('th', rrule.TH, _('Thursday')),
    ('fr', rrule.FR, _('Friday')),
    ('sa', rrule.SA, _('Saturday')),
    ('su', rrule.SU, _('Sunday')),
]
weekday_fields = [info[0] for info in weekday_field_info]

class EventRepeat(models.Model):
    event = models.OneToOneField(Event, related_name='repeat')
    type = models.CharField(max_length=3, choices=repeat.CHOICES)
    until = models.DateField()
    su = models.BooleanField(default=False)
    mo = models.BooleanField(default=False)
    tu = models.BooleanField(default=False)
    we = models.BooleanField(default=False)
    th = models.BooleanField(default=False)
    fr = models.BooleanField(default=False)
    sa = models.BooleanField(default=False)

    def _rrule_weekdays(self):
        return [
            weekday
            for field_name, weekday, _ in weekday_field_info
            if getattr(self, field_name)
        ]

    def get_weekdays_display(self):
        days = [
            day_name
            for field_name, weekday, day_name in weekday_field_info
            if getattr(self, field_name)
        ]
        return ', '.join(unicode(d) for d in days)

    def calc_repeat_rrule(self):
        return repeat.get_rrule(self.type, self.event.date,
                                self.until, self._rrule_weekdays())

class EventDate(models.Model):
    event = models.ForeignKey(Event, related_name='date_set')
    date = models.DateField(db_index=True)
