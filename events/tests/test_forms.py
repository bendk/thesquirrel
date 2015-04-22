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
from datetime import date, time

from django.test import TestCase
from nose.tools import *

from thesquirrel.factories import *
from ..factories import *
from ..forms import EventForm, EventRepeatForm, EventWithRepeatForm
from ..models import EventRepeat, EventRepeatExclude

class EventFormTest(TestCase):
    def test_start_date_must_be_after_end_date(self):
        form = EventForm(data={
            'title': 'test-title',
            'description': 'test-description',
            'date': '1/1/2015',
            'start_time': '18:30',
            'end_time': '16:30',
        })
        assert_false(form.is_valid())

    def test_save(self):
        form = EventForm(data={
            'title': 'test-title',
            'description': 'test-description',
            'location': 'Library',
            'bottomliner': 'Santa',
            'date': '1/1/2015',
            'start_time': '18:30',
            'end_time': '19:30',
        })
        assert_true(form.is_valid())
        user = UserFactory()
        event = form.save(user)
        assert_equal(event.author, user)

class EventRepeatFormTest(TestCase):
    def test_one_weekday_required(self):
        form = EventRepeatForm(data={
            'type': '1M',
            'until': '2/1/2015',
        })
        assert_false(form.is_valid())

    def test_save(self):
        event = EventFactory()
        form = EventRepeatForm(data={
            'type': '1M',
            'until': '2/1/2015',
            'we': 'True',
        })
        assert_true(form.is_valid(), form.errors.as_text())
        repeat = form.save(event)
        assert_equal(repeat.event, event)

    def test_save_with_exclude(self):
        event = EventFactory()
        form = EventRepeatForm(data={
            'type': '1M',
            'until': '2/1/2015',
            'we': 'True',
            'exclude': ['2/4/2015'],
        })
        assert_true(form.is_valid(), form.errors.as_text())
        repeat = form.save(event)
        assert_equal(repeat.event, event)
        assert_equal([e.date for e in repeat.event.excludes.all()],
                     [date(2015, 2, 4)])

    def test_exclude_initial_value(self):
        event = EventFactory(with_repeat=True)
        event.excludes.add(EventRepeatExclude(date=date(2015, 3, 4)))
        form = EventRepeatForm(instance=event.repeat)
        assert_equal(form['exclude'].value(), ['03/04/2015'])

class EventWithRepeatFormTest(TestCase):
    def form_data(self):
        return {
            'title': 'test-title',
            'description': 'test-description',
            'location': 'library',
            'bottomliner': 'Santa',
            'date': '1/1/2015',
            'start_time': '18:30',
            'end_time': '19:30',
            'repeat-type': '',
        }

    def form_data_with_invalid_repeat(self):
        data = self.form_data()
        data.update({
            'repeat-type': '1M',
            # no until or weekdays selected
        })
        return data

    def form_data_with_repeat(self):
        data = self.form_data()
        data.update({
            'repeat-type': '1M',
            'repeat-until': '2/1/2015',
            'repeat-we': True
        })
        return data

    def form_data_with_exclude(self):
        data = self.form_data_with_repeat()
        data.update({
            'repeat-exclude': ['2/4/2015'],
        })
        return data

    def test_no_instance(self):
        form = EventWithRepeatForm()
        assert_is_instance(form.event_form, EventForm)
        assert_is_instance(form.repeat_form, EventRepeatForm)
        assert_equal(form.event_form.instance.id, None)
        assert_equal(form.repeat_form.instance.id, None)

    def test_instance_without_repeat(self):
        event = EventFactory()
        form = EventWithRepeatForm(instance=event)
        assert_equal(form.event_form.instance, event)
        assert_equal(form.repeat_form.instance.id, None)

    def test_instance_with_repeat(self):
        event = EventFactory(with_repeat=True)
        form = EventWithRepeatForm(instance=event)
        assert_equal(form.event_form.instance, event)
        assert_equal(form.repeat_form.instance, event.repeat)

    def test_repeat_form_bound(self):
        # when repeat-type is empty, we shouldn't bind data to the repeat form
        form = EventWithRepeatForm(data=self.form_data())
        assert_false(form.repeat_form.is_bound)
        form = EventWithRepeatForm(data=self.form_data_with_repeat())
        assert_true(form.repeat_form.is_bound)

    def test_validation_without_repeat(self):
        form = EventWithRepeatForm(data={})
        assert_false(form.is_valid())
        form = EventWithRepeatForm(data=self.form_data())
        assert_true(form.is_valid())

    def test_validation_with_repeat(self):
        form = EventWithRepeatForm(data=self.form_data_with_invalid_repeat())
        assert_false(form.is_valid())
        form = EventWithRepeatForm(data=self.form_data_with_repeat())
        assert_true(form.is_valid())

    def test_save_without_repeat(self):
        user = UserFactory()
        form = EventWithRepeatForm(data=self.form_data())
        assert_true(form.is_valid())
        event = form.save(user)
        assert_equal(event.title, 'test-title')
        assert_equal(event.author, user)
        assert_false(event.has_repeat())

    def test_save_with_repeat(self):
        user = UserFactory()
        form = EventWithRepeatForm(data=self.form_data_with_repeat())
        assert_true(form.is_valid())
        event = form.save(user)
        assert_equal(event.title, 'test-title')
        assert_equal(event.author, user)
        assert_true(event.has_repeat())

    def test_save_with_repeat_exclusion(self):
        user = UserFactory()
        form = EventWithRepeatForm(data=self.form_data_with_exclude())
        assert_true(form.is_valid())
        event = form.save(user)
        assert_equal([e.date for e in event.excludes.all()],
                     [date(2015, 2, 4)])

    def test_save_with_deletes_repeat_exclusions(self):
        user = UserFactory()
        event = EventFactory(with_repeat=True)
        # this exclude should be removed when we submit the form data
        event.excludes.add(EventRepeatExclude(date=date(2015, 3, 4)))
        form = EventWithRepeatForm(data=self.form_data_with_exclude(),
                                   instance=event)
        assert_true(form.is_valid())
        event = form.save(user)
        assert_equal([e.date for e in event.excludes.all()],
                     [date(2015, 2, 4)])

    def test_invalid_exclude(self):
        user = UserFactory()
        data = self.form_data_with_repeat()
        data['repeat-exclude'] = ['invalid-date']
        form = EventWithRepeatForm(data=data)
        assert_false(form.is_valid())

    def test_save_without_repeat_deletes_existing_repeat(self):
        event = EventFactory(with_repeat=True)
        user = UserFactory()
        form = EventWithRepeatForm(data=self.form_data(), instance=event)
        assert_true(form.is_valid())
        event = form.save(user)
        # since the form didn't have repeat data, we should delete the repeat
        assert_false(EventRepeat.objects.filter(event=event).exists())

    def test_save_without_repeat_deletes_existing_exclude(self):
        event = EventFactory(with_repeat=True)
        event.excludes.add(EventRepeatExclude(date=date(2015, 3, 4)))
        user = UserFactory()
        form = EventWithRepeatForm(data=self.form_data(), instance=event)
        assert_true(form.is_valid())
        event = form.save(user)
        # since the form didn't have repeat data, we should delete the exclude
        # date
        assert_false(event.excludes.all().exists())
