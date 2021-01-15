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
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from dateutil import rrule

from editor.fields import EditorTextField
from . import repeat
from .utils import format_time

class EventTimeMixin(object):
    def get_start_time_display(self):
        return format_time(self.start_time)

    def get_end_time_display(self):
        return format_time(self.end_time)

    def get_time_display(self):
        return '{} - {}'.format(self.get_start_time_display(),
                                self.get_end_time_display())

class Event(models.Model, EventTimeMixin):
    title = models.CharField(max_length=255)
    description = EditorTextField()
    location = models.CharField(max_length=255)
    bottomliner = models.CharField(max_length=255)
    created = models.DateTimeField(default=timezone.now)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    space_request = models.ForeignKey('SpaceUseRequest', models.CASCADE,
                                      null=True)

    def __str__(self):
        return u'Event: {}'.format(self.title)

    def update_calendar_items(self):
        self.calendar_items.all().delete()
        excludes = set(e.date for e in self.excludes.all())
        to_create = [
            CalendarItem(event=self, date=self.date,
                         start_time=self.start_time,
                         end_time=self.end_time)
        ]
        # Often the event and repeat share a start date, in that case don't
        # create a duplicate date.
        excludes.add(self.date)
        to_create.extend([
            CalendarItem(event=self, date=dt.date(),
                         start_time=repeat.start_time,
                         end_time=repeat.end_time)
            for repeat in self.repeat_set.all()
            for dt in repeat.calc_repeat_rrule()
            if dt.date() not in excludes
        ])
        CalendarItem.objects.bulk_create(to_create)

    def get_date_display(self):
        return '{d:%a} {d.month}/{d.day}/{d.year}'.format(d=self.date)

    def get_when_text(self):
        repeats = self.repeat_set.all()
        if repeats:
            return [
                _('{repeat_type} at {days}, {start_time} - {end_time}').format(
                    repeat_type=repeat.get_type_display(),
                    days=repeat.get_weekdays_display(),
                    start_time=repeat.get_start_time_display(),
                    end_time=repeat.get_end_time_display(),
                )
                for repeat in repeats
            ]
        else:
            return [
                _('{date}, {start_time}-{end_time}').format(
                    date=self.get_date_display(),
                    start_time=self.get_start_time_display(),
                    end_time=self.get_end_time_display(),
                ),
            ]

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

class EventRepeat(models.Model, EventTimeMixin):
    event = models.ForeignKey(Event, models.CASCADE, related_name='repeat_set')
    type = models.CharField(max_length=3, choices=repeat.CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
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
        return ', '.join(str(d) for d in days)

    def calc_repeat_rrule(self):
        return repeat.get_rrule(self.type, self.start_date,
                                self.end_date, self._rrule_weekdays())

class EventRepeatExclude(models.Model):
    event = models.ForeignKey(Event, models.CASCADE, related_name='excludes')
    date = models.DateField(unique=True)

class CalendarItem(models.Model, EventTimeMixin):
    """Represents an entry in the calendar."""

    event = models.ForeignKey(Event, models.CASCADE,
                              related_name='calendar_items')
    date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    @classmethod
    def upcoming(cls):
        today = timezone.now().date()
        return (
            cls.objects
            .filter(date__gte=today)
            .filter(Q(event__space_request__isnull=True) |
                    Q(event__space_request__state=SpaceUseRequest.APPROVED))
            .select_related('event')
            .order_by('date', 'event__start_time'))

    @property
    def space_request(self):
        return self.event.space_request

class SpaceUseRequestQueryset(models.QuerySet):
    def iter_subclassses(self):
        return (request.get_subclass() for request in self)

    def current(self):
        changed_since = timezone.now() - timedelta(days=14)
        case_sql = ('(CASE WHEN state="P" THEN 0 '
                    'WHEN state="B" THEN 1 '
                    'ELSE 2 END)')
        return (self.filter(~Q(list=SpaceUseRequest.COMPLETE) |
                            Q(changed__gte=changed_since))
                .extra(select={
                    'state_order':'(CASE WHEN state="P" THEN 0 ELSE 1 END)',
                }).order_by('state_order', 'created'))

class SpaceUseRequestManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('singlespaceuserequest',
                                                     'ongoingspaceuserequest')

    def lookup_others(self, other_request):
        return (self
                .filter(Q(name=other_request.name)|
                        Q(email=other_request.email)|
                        Q(phone_number=other_request.phone_number))
                .exclude(id=other_request.id))

class SpaceUseRequest(models.Model):
    PENDING = 'P'
    APPROVED = 'A'
    DECLINED = 'D'
    CANCLED = 'C'
    STATE_CHOICES = (
        (PENDING, _('Pending')),
        (APPROVED, _('Approved')),
        (DECLINED, _('Declined')),
        (CANCLED, _('Canceled')),
    )

    INBOX = 'I'
    WAITING_FOR_THEM = 'W'
    NEEDS_DISCUSSION = 'N'
    COMING_TO_MEETING = 'M'
    NEEDS_BOTTOMLINER = 'B'
    COMPLETE = 'C'
    LIST_CHOICES = (
        (INBOX, 'Inbox'),
        (WAITING_FOR_THEM, 'Waiting for them'),
        (NEEDS_DISCUSSION, 'Needs discussion'),
        (COMING_TO_MEETING, 'Coming to meeting'),
        (NEEDS_BOTTOMLINER, 'Needs bottomliner'),
        (COMPLETE, 'Complete'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    state = models.CharField(max_length=1, choices=STATE_CHOICES,
                             default=PENDING)
    list = models.CharField(max_length=1, choices=LIST_CHOICES,
                            default=INBOX)
    created = models.DateTimeField(default=timezone.now)
    deposit_paid = models.BooleanField(default=False)
    has_bottomliner = models.BooleanField(default=False)
    changed = models.DateTimeField(null=True, auto_now=True)
    name = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(max_length=255, db_index=True)
    squirrel_member = models.CharField(max_length=255, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    website = models.CharField(max_length=255, blank=True)
    mission = models.TextField(blank=True)
    phone_number = models.CharField(max_length=255, db_index=True)
    additional_comments = models.TextField(blank=True)

    objects = SpaceUseRequestManager.from_queryset(SpaceUseRequestQueryset)()

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

    def is_declined(self):
        return self.state == self.DECLINED

    def is_canceled(self):
        return self.state == self.CANCLED

    def has_event(self):
        return bool(self.event_set.all())

    def get_subclass(self):
        """
        Get a SingleSpaceUseRequest or OngoingSpaceUseRequest instance
        """
        if hasattr(self, 'singlespaceuserequest'):
            return self.singlespaceuserequest
        elif hasattr(self, 'ongoingspaceuserequest'):
            return self.ongoingspaceuserequest
        else:
            raise TypeError("No subclass found: {}".format(instance))

    def get_created_display(self):
        created = timezone.localtime(self.created)
        return '{d:%a} {d.month}/{d.day}, {t}'.format(
            d=created, t=format_time(created.time()))

    def update_state(self, deposit_paid, has_bottomliner, new_state, new_list):
        self.deposit_paid = deposit_paid
        self.has_bottomliner = has_bottomliner
        self.state = new_state
        self.list = new_list
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

    def get_note(self):
        """
        Get a note for this request.

        This is text that we send out for emails describing the event
        """
        return self.title


    list_order = [
        INBOX,
        WAITING_FOR_THEM,
        COMING_TO_MEETING,
        NEEDS_DISCUSSION,
        NEEDS_BOTTOMLINER,
        COMPLETE,
    ]

    @classmethod
    def get_lists(cls):
        all_requests = cls.objects.current().iter_subclassses()
        request_lists = []
        for list_code in cls.list_order:
            requests = [r for r in all_requests if r.list == list_code]
            if requests:
                request_lists.append((requests[0].get_list_display(), requests))
        return request_lists

class SingleSpaceUseRequest(SpaceUseRequest):
    event_type = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    setup_time = models.CharField(max_length=255, blank=True)
    cleanup_time = models.CharField(max_length=255, blank=True)
    event_charge = models.CharField(max_length=255)
    squirrel_donation = models.TextField(blank=True)
    number_of_people = models.CharField(max_length=255)
    space_needs = models.TextField()

    objects = models.Manager.from_queryset(SpaceUseRequestQueryset)()

    type = 'single'
    def get_type_display(self):
        return _('Single use')

    def get_date_object(self):
        """
        Gets the object to use for the event date.  This is either the
        space request, or an event created for the request.
        """
        events = self.event_set.all()
        if len(events) == 1:
            return events[0]
        else:
            return self

    def calc_date(self):
        return self.get_date_object().date

    def get_date_display(self):
        date_obj = self.get_date_object()

        return '{d:%a} {d.month}/{d.day}, {st}-{et}'.format(
            d=date_obj.date, st=format_time(date_obj.start_time),
            et=format_time(date_obj.end_time))

    def calendar_items_on_date(self):
        valid_states = [
            SpaceUseRequest.PENDING,
            SpaceUseRequest.APPROVED,
        ]
        rv = []
        for item in CalendarItem.objects.filter(date=self.calc_date()):
            if item.space_request:
                if (item.space_request.id != self.id and
                    item.space_request.state in valid_states):
                    rv.append(item)
            else:
                rv.append(item)
        return rv

    def guess_best_date(self):
        """
        Guess the date based on the date submitted and the linked events
        """
        return self.get_date_display()

    def get_note(self):
        lines = [
            self.title,
            'Single use',
            self.name,
            settings.BASE_URL + self.get_absolute_url(),
        ]
        lines.append(self.get_date_display())
        if self.additional_comments:
            lines.extend(['', self.additional_comments])
        return '\n'.join(lines)

class OngoingSpaceUseRequest(SpaceUseRequest):
    dates = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    squirrel_goals = models.TextField()
    space_needs = models.CharField(max_length=255)

    objects = models.Manager.from_queryset(SpaceUseRequestQueryset)()

    type = 'ongoing'
    def get_type_display(self):
        return _('Ongoing use')

    def get_date_display(self):
        return self.dates

    def get_note(self):
        lines = [
            self.title,
            'Ongoing use',
            self.name,
            self.frequency,
            settings.BASE_URL + self.get_absolute_url(),
        ]
        if self.additional_comments:
            lines.extend(['', self.additional_comments])
        return '\n'.join(lines)

class SpaceUseNote(models.Model):
    space_use_request = models.ForeignKey(SpaceUseRequest,
                                          models.CASCADE,
                                          related_name='notes')
    user = models.ForeignKey(User, models.CASCADE)
    datetime = models.DateTimeField(default=timezone.now)
    body = models.TextField()

    class Meta:
        ordering = ['datetime']
