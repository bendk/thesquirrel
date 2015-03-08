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

from .models import Event, weekday_strings
from . import repeat

class DateField(forms.DateField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = forms.DateInput(attrs={'class': 'date'})
        super(forms.DateField, self).__init__(*args, **kwargs)

class TimeField(forms.TimeField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = forms.TimeInput(attrs={'class': 'time'})
        super(forms.TimeField, self).__init__(*args, **kwargs)

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            'title', 'body', 'date', 'start_time', 'end_time',
            'repeat_type', 'repeat_until',
            'repeat_mo', 'repeat_tu', 'repeat_we', 'repeat_th', 'repeat_fr',
            'repeat_sa', 'repeat_su',
        )
        labels = {
            'repeat_mo': _('Mon'),
            'repeat_tu': _('Tue'),
            'repeat_we': _('Wed'),
            'repeat_th': _('Thu'),
            'repeat_fr': _('Fri'),
            'repeat_sa': _('Sat'),
            'repeat_sun': _('Sun'),
        }

    def clean(self):
        cleaned_data = super(EventForm, self).clean()
        cleaned_data['repeat_weekdays'] = [
            day for day in weekday_strings
            if cleaned_data['repeat_{}'.format(day)]
        ]

        if cleaned_data['end_time'] < cleaned_data['start_time']:
            self.add_error('end_time', forms.ValidationError(
                _('End time before starte time'), code='end-time-to-early'))


        if cleaned_data.get('repeat_type'):
            if not cleaned_data['repeat_weekdays']:
                self.add_error('repeat_type', forms.ValidationError(
                    _('No days selected'), code='no-weekdays'))
            if not cleaned_data['repeat_until']:
                self.add_error('repeat_until', forms.ValidationError(
                    _('This field is required'), code='required'))
        return cleaned_data

    def save(self, user):
        event = super(EventForm, self).save(commit=False)
        event.author = user
        event.save()
        event.update_dates()
        return event
