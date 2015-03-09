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
from dateutil import rrule

from editor.fields import EditorTextField
from . import repeat

# map the strings we use for weekday fields to rrule classes
rrule_weekday_map = {
    'mo': rrule.MO,
    'tu': rrule.TU,
    'we': rrule.WE,
    'th': rrule.TH,
    'fr': rrule.FR,
    'sa': rrule.SA,
    'su': rrule.SU,
}
weekday_strings = rrule_weekday_map.keys()

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

    def has_repeat(self):
        try:
            self.repeat
        except EventRepeat.DoesNotExist:
            return False
        else:
            return True

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
            for field_name, weekday in rrule_weekday_map.items()
            if getattr(self, field_name)
        ]

    def calc_repeat_rrule(self):
        return repeat.get_rrule(self.type, self.event.date,
                                self.until, self._rrule_weekdays())

class EventDate(models.Model):
    event = models.ForeignKey(Event, related_name='date_set')
    date = models.DateField(db_index=True)
