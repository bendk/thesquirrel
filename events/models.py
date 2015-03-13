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

from __future__ import absolute_import
from datetime import timedelta

from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
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

class SpaceUseRequestQueryset(models.QuerySet):
    def iterator(self):
        # This code does a couple things:
        #   - Generate subclass instances instead of the base class
        #   - Only uses 1 query to fetch all the data we need
        real_query = self.select_related('singlespaceuserequest',
                                         'ongoingspaceuserequest')
        for base_obj in super(SpaceUseRequestQueryset, real_query).iterator():
            if base_obj._singlespaceuserequest_cache:
                yield base_obj.singlespaceuserequest
            elif base_obj._ongoingspaceuserequest_cache:
                yield base_obj.ongoingspaceuserequest
            else:
                raise TypeError("No subclass found: {}".format(base_obj))


class SpaceUseRequestManager(models.Manager):
    def get_queryset(self):
        return SpaceUseRequestQueryset(self.model)

    def current(self):
        changed_since = timezone.now() - timedelta(days=14)
        return (self.filter(Q(state=SpaceUseRequest.PENDING) |
                            Q(changed__gte=changed_since))
                .extra(select={
                    'state_order':'(CASE WHEN state="P" THEN 0 ELSE 1 END)',
                }).order_by('state_order', 'created'))

class SpaceUseRequest(models.Model):
    PENDING = 'P'
    APPROVED = 'A'
    DENIED = 'D'
    STATE_CHOICES = (
        (PENDING, _('Pending')),
        (APPROVED, _('Approved')),
        (DENIED, _('Denied')),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    state = models.CharField(max_length=1, choices=STATE_CHOICES,
                             default=PENDING)
    created = models.DateTimeField(default=timezone.now)
    changed = models.DateTimeField(null=True, auto_now=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    squirrel_member = models.CharField(max_length=255, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    website = models.CharField(max_length=255, blank=True)
    mission = models.TextField(blank=True)
    phone_number = models.CharField(max_length=255)
    additional_comments = models.TextField(blank=True)

    objects = SpaceUseRequestManager()

    class Meta:
        index_together = [
            ('state', 'changed'),
        ]

    def get_absolute_url(self):
        return reverse('events:space-request', args=(self.id,))

    def is_pending(self):
        return self.state == self.PENDING

    def is_approved(self):
        return self.state == self.APPROVED

    def is_denied(self):
        return self.state == self.DENIED

    def get_created_display(self):
        created = timezone.localtime(self.created)
        return '{d:%a} {d.month}/{d.day}, {t}'.format(
            d=created, t=format_time(created.time()))

    def approve(self):
        self.state = self.APPROVED
        self.save()

    def deny(self):
        self.state = self.DENIED
        self.save()

    def send_email(self, request):
        events_email = getattr(settings, 'EVENTS_EMAIL', None)
        if not events_email:
            return
        message = render_to_string('events/new-space-use-request-email.txt', {
            'space_use_request': self,
            'uri': request.build_absolute_uri(self.get_absolute_url()),
        })
        send_mail('New space use request', message, self.email,
                  [events_email], fail_silently=False)

class SingleSpaceUseRequest(SpaceUseRequest):
    event_type = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    setup_cleanup_time = models.CharField(max_length=255, blank=True)
    event_charge = models.CharField(max_length=255)
    squirrel_donation = models.TextField(blank=True)

    type = 'single'
    def get_type_display(self):
        return _('Single use')

    def get_date_display(self):
        return '{d:%a} {d.month}/{d.day}, {st}-{et}'.format(
            d=self.date, st=format_time(self.start_time),
            et=format_time(self.end_time))

class OngoingSpaceUseRequest(SpaceUseRequest):
    dates = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    squirrel_goals = models.TextField()
    space_needs = models.CharField(max_length=255)

    type = 'ongoing'
    def get_type_display(self):
        return _('Ongoing use')

    def get_date_display(self):
        return self.dates


class SpaceUseNote(models.Model):
    space_use_request = models.ForeignKey(SpaceUseRequest,
                                          related_name='notes')
    user = models.ForeignKey(User)
    datetime = models.DateTimeField(default=timezone.now)
    body = models.TextField()
