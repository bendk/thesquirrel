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
from datetime import datetime, time
import itertools

from dateutil.relativedelta import relativedelta
from django import forms
from django.forms.util import ErrorDict
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from . import repeat
from .models import (Event, EventRepeat, EventRepeatExclude,
                     weekday_fields, SpaceUseRequest, SingleSpaceUseRequest,
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

class MultipleDateField(forms.Field):
    hidden_widget = forms.MultipleHiddenInput
    widget = forms.MultipleHiddenInput
    default_error_messages = forms.DateField.default_error_messages.copy()

    def to_python(self, value):
        "Returns a Unicode object."
        if value in self.empty_values:
            return []
        try:
            return [
                datetime.strptime(item, '%m/%d/%Y').date()
                for item in value
            ]
        except ValueError:
            raise forms.ValidationError(self.error_messages['invalid'],
                                        code='invalid')

    def prepare_value(self, value):
        if value in self.empty_values:
            return []
        return [ date.strftime('%m/%d/%Y') for date in value ]

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

    def save(self, update_calendar_items=True):
        event = super(EventForm, self).save(commit=False)
        event.save()
        if update_calendar_items:
            event.update_calendar_items()
        return event

def two_years_from_now():
    return (timezone.now() + relativedelta(years=2)).date()

class EventRepeatForm(forms.ModelForm):
    TYPE_CHOICES = [
        ('', _("No repeat")),
    ] + repeat.CHOICES

    type = forms.ChoiceField(choices=TYPE_CHOICES, label='')
    end_date = DateField(initial=two_years_from_now)
    start_date = DateField()
    start_time = TimeField(initial='18:00:00')
    end_time = TimeField(initial='19:00:00')

    def __init__(self, number, *args, **kwargs):
        super(EventRepeatForm, self).__init__(*args, **kwargs)
        self.updating = kwargs.get('instance') is not None
        self.number = number
        self.setup_empty_type_label()
        if number > 1:
            self.heading = _('Repeat #{number}').format(number=number)
        else:
            self.heading = _('Repeat')

    class Meta:
        model = EventRepeat
        fields = (
            'type', 'start_date', 'end_date', 'start_time', 'end_time',
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

    def setup_empty_type_label(self):
        field = self.fields['type']
        new_choices = []
        for value, label in field.choices:
            if value == '':
                if self.updating:
                    label = _('Delete repeat')
                else:
                    label = _('No repeat')
            new_choices.append((value, label))
        field.choices = new_choices


    def full_clean(self):
        if self.is_bound and self.type_is_empty():
            # skip any other validation in this case
            self._errors = ErrorDict()
            self.cleaned_data = {}
        else:
            super(EventRepeatForm, self).full_clean()

    def clean(self):
        if not self.any_day_selected():
            self.add_error('type', forms.ValidationError(
                _('No days selected'), code='no-weekdays'))
        return self.cleaned_data

    def type_is_empty(self):
        return self.data.get(self.add_prefix('type')) == ''

    def any_day_selected(self):
        return any(day for day in weekday_fields if self.cleaned_data[day])

    def save(self, event):
        if self.type_is_empty():
            if self.updating:
                self.instance.delete()
            return
        repeat = super(EventRepeatForm, self).save(commit=False)
        repeat.event = event
        repeat.save()
        return repeat

class EventRepeatExcludeForm(forms.Form):
    dates = MultipleDateField(required=False)

    def save(self, event):
        event.excludes.all().delete()
        event.excludes.bulk_create(
            EventRepeatExclude(event=event, date=date)
            for date in set(self.cleaned_data['dates'])
        )

class CompositeEventForm(object):
    """Form-like object that handles an EventForm, multiple
    EventRepeatForms, and a EventRepeatExcludeForm.
    """

    def __init__(self, event=None, data=None):
        self.event_form = EventForm(prefix='event', instance=event, data=data)
        self.make_exclude_form(event, data)
        self.make_repeat_forms(event, data)

    def make_exclude_form(self, event, data):
        if event:
            initial = {
                'dates': [e.date for e in event.excludes.all()]
            }
        else:
            initial = None
        print initial
        self.exclude_form = EventRepeatExcludeForm(
            prefix='exclude', initial=initial, data=data,
        )

    def make_repeat_forms(self, event, data):
        counter = itertools.count(1)
        if event:
            self.update_repeat_forms = [
                EventRepeatForm(
                    prefix='repeat-update-{}'.format(i),
                    number=counter.next(), instance=repeat, data=data
                )
                for i, repeat in enumerate(event.repeat_set.all())
            ]
        else:
            self.update_repeat_forms = []

        self.repeat_forms = [
            EventRepeatForm(prefix='repeat-create-{}'.format(i),
                            number=counter.next(), data=data)
            for i in range(5)
        ]

    def is_valid(self):
        all_forms = [self.event_form, self.exclude_form]
        all_forms.extend(self.repeat_forms)
        all_forms.extend(self.update_repeat_forms)

        return all([f.is_valid() for f in all_forms])

    def save(self):
        event = self.event_form.save(update_calendar_items=False)
        for form in self.repeat_forms + self.update_repeat_forms:
            form.save(event)
        self.exclude_form.save(event)
        event.update_calendar_items()
        return event

class SingleSpaceRequestForm(forms.ModelForm):
    date = DateField()
    start_time = TimeField(with_blank=True, initial='')
    end_time = TimeField(with_blank=True, initial='')

    class Meta:
        model = SingleSpaceUseRequest
        fields = (
            'title', 'event_type', 'description', 'date', 'start_time',
            'end_time', 'setup_time', 'cleanup_time', 'event_charge',
            'squirrel_donation', 'name', 'email', 'squirrel_member',
            'organization', 'website', 'mission', 'phone_number',
            'additional_comments',
        )
        labels = {
            'title': _('Event title'),
            'setup_time': _('What time do you want to setup for the event?'),
            'cleanup_time': _('How long do you need to cleanup the event?'),
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

class SpaceRequestUpdateForm(forms.Form):
    note = forms.CharField(
        label=_('Add note'), required=False, 
        widget=forms.Textarea(attrs={'rows': 3}))
    state = forms.ChoiceField(choices=SpaceUseRequest.STATE_CHOICES,
                              required=False)

    def __init__(self, space_request, user, data=None):
        self.space_request = space_request
        self.user = user
        super(SpaceRequestUpdateForm, self).__init__(
            initial=dict(state=space_request.state),
            data=data,
        )

    def save(self):
        self.space_request.update_state(self.cleaned_data['state'])
        if self.cleaned_data['note']:
            self.space_request.notes.create(user=self.user,
                                            body=self.cleaned_data['note'])
