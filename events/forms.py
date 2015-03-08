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

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Event, EventRepeat, weekday_strings
from . import repeat

class DateField(forms.DateField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = forms.DateInput(attrs={'class': 'pikaday'},
                                           format='%m/%d/%y')
        super(forms.DateField, self).__init__(*args, **kwargs)

class TimeField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        choices = []
        for h in range(23):
            if h < 12:
                period = 'am'
            else:
                period = 'pm'
            h_12 = ((h-1) % 12) + 1
            for m in (0, 30):
                choices.append(('{:0>2d}:{:0>2d}'.format(h, m),
                                '{}:{:0>2d}{}'.format(h_12, m, period)))
        kwargs['choices'] = choices
        kwargs['initial'] = '18:00'
        super(TimeField, self).__init__(*args, **kwargs)

class EventForm(forms.ModelForm):
    date = DateField()
    start_time = TimeField()
    end_time = TimeField()

    class Meta:
        model = Event
        fields = (
            'title', 'body', 'date', 'start_time', 'end_time',
        )
        labels = {
            'body': '',
        }

    def clean(self):
        cleaned_data = super(EventForm, self).clean()

        if ('end_time' in cleaned_data and 'start_time' in cleaned_data and
            cleaned_data['end_time'] < cleaned_data['start_time']):
            self.add_error('end_time', forms.ValidationError(
                _('End time before starte time'), code='end-time-to-early'))

        return cleaned_data

    def save(self, user):
        event = super(EventForm, self).save(commit=False)
        event.author = user
        event.save()
        event.update_dates()
        return event

class EventRepeatForm(forms.ModelForm):
    TYPE_CHOICES = [
        ('', _("Don't Repeat")),
    ] + repeat.CHOICES

    type = forms.ChoiceField(choices=TYPE_CHOICES)
    until = DateField()

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
        if not any(day for day in weekday_strings if cleaned_data[day]):
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
        event = self.event_form.save(user)
        if self.repeat_form.is_bound:
            self.repeat_form.save(event)
        elif event.has_repeat():
            event.repeat.delete()
        return event
