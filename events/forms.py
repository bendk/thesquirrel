# thesquirrel.org
#
# Copyright (C) 2015 Flying Squirrel Community Space
#
# thesquirrel.org is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
# thesquirrel.org is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with thesquirrel.org.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from datetime import time

from dateutil.relativedelta import relativedelta
from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from . import repeat
from .models import (Event, EventRepeat, weekday_fields,
                     SpaceUseRequest, SingleSpaceUseRequest,
                     OngoingSpaceUseRequest)
from .utils import format_time

class DateField(forms.DateField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = forms.DateInput(attrs={'class': 'pikaday'},
                                           format='%m/%d/%Y')
        super(forms.DateField, self).__init__(*args, **kwargs)

class TimeField(forms.TimeField):
    def __init__(self, *args, **kwargs):
        choices = []
        if kwargs.pop('with_blank', False):
            choices.append(('', ''))
        for h in range(7, 24):
            for m in (0, 30):
                t = time(h, m)
                choices.append((t.strftime('%H:%M:00'), format_time(t)))
        kwargs['widget'] = forms.Select(choices=choices)
        super(TimeField, self).__init__(*args, **kwargs)

class EventForm(forms.ModelForm):
    date = DateField()
    start_time = TimeField(initial='18:00:00')
    end_time = TimeField(initial='19:00:00')

    class Meta:
        model = Event
        fields = (
            'title', 'description', 'location', 'bottomliner',
            'date', 'start_time', 'end_time',
        )
        labels = {
            'description': '',
            'description': '',
        }

    def clean(self):
        cleaned_data = super(EventForm, self).clean()

        if ('end_time' in cleaned_data and 'start_time' in cleaned_data and
            cleaned_data['end_time'] < cleaned_data['start_time']):
            self.add_error('end_time', forms.ValidationError(
                _('End time before starte time'), code='end-time-to-early'))

        return cleaned_data

    def save(self, user, update_dates=True):
        event = super(EventForm, self).save(commit=False)
        event.author = user
        event.save()
        if update_dates:
            event.update_dates()
        return event

def two_years_from_now():
    return (timezone.now() + relativedelta(years=2)).date()

class EventRepeatForm(forms.ModelForm):
    TYPE_CHOICES = [
        ('', _("Don't Repeat")),
    ] + repeat.CHOICES

    type = forms.ChoiceField(choices=TYPE_CHOICES, label='')
    until = DateField(initial=two_years_from_now)

    class Meta:
        model = EventRepeat
        fields = (
            'type', 'until',
            'mo', 'tu', 'we', 'th', 'fr', 'sa', 'su',
        )
        labels = {
            'mo': _('Mon'),
            'tu': _('Tue'),
            'we': _('Wed'),
            'th': _('Thu'),
            'fr': _('Fri'),
            'sa': _('Sat'),
            'su': _('Sun'),
        }

    def enabled(self):
        return self.data['type'] != ''

    def clean(self):
        cleaned_data = super(EventRepeatForm, self).clean()
        if not any(day for day in weekday_fields if cleaned_data[day]):
            self.add_error('type', forms.ValidationError(
                _('No days selected'), code='no-weekdays'))
        return cleaned_data

    def save(self, event):
        repeat = super(EventRepeatForm, self).save(commit=False)
        repeat.event = event
        repeat.save()
        return repeat

class EventWithRepeatForm(object):
    """Form-like object that handles both the EventForm and
    EventRepeatForm.
    """

    def __init__(self, instance=None, data=None):
        if instance and instance.has_repeat():
            repeat = instance.repeat
        else:
            repeat = None
        if data and data.get('repeat-type'):
            repeat_data = data
        else:
            repeat_data = None
        self.event_form = EventForm(instance=instance, data=data)
        self.repeat_form = EventRepeatForm(prefix='repeat', instance=repeat,
                                           data=repeat_data)

    def is_valid(self):
        if not self.repeat_form.is_bound:
            # just need to validate the event form
            return self.event_form.is_valid()
        else:
            # need to validate both forms, make sure we clean both
            self.event_form.full_clean()
            self.repeat_form.full_clean()
            return self.event_form.is_valid() and self.repeat_form.is_valid()

    def save(self, user):
        event = self.event_form.save(user, update_dates=False)
        if self.repeat_form.is_bound:
            self.repeat_form.save(event)
        elif event.has_repeat():
            event.repeat.delete()
        event.update_dates()
        return event

class SingleSpaceRequestForm(forms.ModelForm):
    date = DateField()
    start_time = TimeField(with_blank=True, initial='')
    end_time = TimeField(with_blank=True, initial='')

    class Meta:
        model = SingleSpaceUseRequest
        fields = (
            'title', 'event_type', 'description', 'date', 'start_time',
            'end_time', 'setup_cleanup_time', 'event_charge',
            'squirrel_donation', 'name', 'email', 'squirrel_member',
            'organization', 'website', 'mission', 'phone_number',
            'additional_comments',
        )
        labels = {
            'title': _('Event title'),
            'setup_cleanup_time': _('Do you need extra setup/cleanup time? '
                                    'If so, how much?'),
            'event_charge': _('Will you ask for donations?'),
            'squirrel_donation': _('If you are collecting money for your '
                                   'event, does our standard donation '
                                   'agreement work for you? If not, what '
                                   'would you like to propose?'),
            'squirrel_member': _('Are you a member of the FSCS or have a '
                                 'contact in the collective? If so, who?'),
            'organization': _('Organization Name'),
            'website': _('Website URL'),
            'mission': _('Mission Statement'),
            'additional_comments': '',
        }
        help_texts = {
            'event_charge': _(
                'We ask that events request donations instead of charging '
                'fees and that no one be turned away for lack of funds.'),
        }

class OngoingSpaceRequestForm(forms.ModelForm):
    class Meta:
        model = OngoingSpaceUseRequest
        fields = (
            'title', 'description', 'dates', 'frequency',
            'squirrel_goals', 'space_needs', 'name', 'email',
            'squirrel_member', 'organization', 'website', 'mission',
            'phone_number', 'additional_comments',
        )

        labels = {
            'title': _('Event title'),
            'dates': _('Date and times'),
            'frequency': _('Frequency of use (weekly, monthly, etc)'),
            'squirrel_goals': _('How will your use of the space advance '
                                'the goals of the center'),
            'space_needs': _('Material needs of the space (chairs, stage, '
                             'sound system, desks, table, kitchen use, etc)'),
            'squirrel_member': _('Are you a member of the FSCS or have a '
                                 'contact in the collective? If so, who?'),
            'organization': _('Organization Name'),
            'website': _('Website URL'),
            'mission': _('Mission Statement'),
            'additional_comments': '',
        }
        help_texts = {
            'event_charge': _('If you do, we ask that no one be turned away '
                              'for lack of funds.'),
        }

class SpaceRequestStateForm(forms.Form):
    state = forms.ChoiceField(choices=SpaceUseRequest.STATE_CHOICES)

    def __init__(self, space_request, data=None):
        self.space_request = space_request
        super(SpaceRequestStateForm, self).__init__(
            initial=dict(state=space_request.state),
            data=data,
        )

    def save(self):
        self.space_request.update_state(self.cleaned_data['state'])
