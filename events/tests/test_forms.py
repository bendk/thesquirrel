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
import mock

from django.test import TestCase
from nose.tools import *

from thesquirrel.factories import *
from ..factories import *
from ..forms import (EventForm, EventRepeatForm, EventRepeatExcludeForm,
                     CompositeEventForm)
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
        form.save()

class EventRepeatFormTest(TestCase):
    def make_form(self, update=False, number=1):
        if update:
            event = EventFactory(with_repeat=True)
            instance = event.repeat_set.all().get()
        else:
            event = EventFactory()
            instance = None
        return EventRepeatForm(number, instance=instance)

    def make_form_with_data(self, update=False, no_days=False,
                            empty_type=False, number=1):
        if update:
            event = EventFactory(with_repeat=True)
            instance = event.repeat_set.all().get()
        else:
            event = EventFactory()
            instance = None
        data = {
            'type': '1M' if not empty_type else '',
            'start_date': '1/1/2015',
            'we': True if not no_days else False,
            'end_date': '2/1/2015',
            'start_time': '16:30',
            'end_time': '18:30',
        }
        return EventRepeatForm(number, instance=instance, data=data)

    def test_save(self):
        form = self.make_form_with_data()
        assert_true(form.is_valid(), form.errors.as_text())
        event = EventFactory()
        repeat = form.save(event)
        assert_equal(repeat.event, event)

    def test_one_weekday_required(self):
        form = self.make_form_with_data(no_days=True)
        assert_false(form.is_valid())

    def test_empty_type_doesnt_create_new(self):
        form = self.make_form_with_data(empty_type=True)
        assert_true(form.is_valid(), form.errors.as_text())
        event = EventFactory()
        form.save(event)
        assert_false(event.repeat_set.all().exists())

    def test_empty_type_deletes_existing(self):
        form = self.make_form_with_data(update=True, empty_type=True)
        assert_true(form.is_valid(), form.errors.as_text())
        event = EventFactory()
        form.save(event)
        assert_false(event.repeat_set.all().exists())

    def check_empty_type_label(self, form, correct_label):
        empty_type_label = None
        for value, label in form.fields['type'].choices:
            if value == '':
                empty_type_label = unicode(label)
                break
        assert_not_equal(empty_type_label, None)
        assert_equal(empty_type_label, correct_label)

    def test_empty_type_labels(self):
        form = self.make_form()
        self.check_empty_type_label(self.make_form(), u'No repeat')
        self.check_empty_type_label(self.make_form(update=True),
                                    u'Delete repeat')

    def test_headings(self):
        assert_equal(self.make_form().heading, 'Repeat')
        assert_equal(self.make_form(number=2).heading, 'Repeat #2')

class EventRepeatExcludeFormTest(TestCase):
    def test_create_excludes(self):
        event = EventFactory(with_repeat=True, with_exclude=True)
        form = EventRepeatExcludeForm(data={
            'dates': ['2/4/2015', '2/5/2015'],
        })
        assert_true(form.is_valid())
        form.save(event)

    def test_invalid_value(self):
        form = EventRepeatExcludeForm(data={
            'dates': ['invalid-date'],
        })
        assert_false(form.is_valid())

class CompositeEventFormTest(TestCase):
    def test_initial_excludes(self):
        event = EventFactory(with_repeat=True, with_exclude=True)
        form = CompositeEventForm(event)
        assert_equal(form.exclude_form.initial['dates'], [
            e.date for e in event.excludes.all()
        ])

    def mock_out_subforms(self, composite_form):
        def mock_subform():
            return mock.Mock(
                is_valid=mock.Mock(return_value=True),
            )

        composite_form.repeat_form = mock_subform()
        composite_form.event_form = mock_subform()
        composite_form.exclude_form = mock_subform()
        for i in range(len(composite_form.update_repeat_forms)):
            composite_form.update_repeat_forms[i] = mock_subform()
        return composite_form

    def test_is_valid(self):
        event = EventFactory(with_repeat=True)
        form = self.mock_out_subforms(CompositeEventForm(event))
        assert_true(form.is_valid())
        assert_true(form.event_form.is_valid.called)
        assert_true(form.repeat_form.is_valid.called)
        for repeat_form in form.update_repeat_forms:
            assert_true(repeat_form.is_valid.called)

    def test_is_valid_return_false(self):
        event = EventFactory(with_repeat=True)
        form = self.mock_out_subforms(CompositeEventForm(event))
        form.event_form.is_valid.return_value = False
        assert_false(form.is_valid())
        # Even though event_form.is_valid() returns False, we should still
        # call is_valid for each subform so that the ErrorDict is generated.
        assert_true(form.event_form.is_valid.called)
        assert_true(form.repeat_form.is_valid.called)
        for repeat_form in form.update_repeat_forms:
            assert_true(repeat_form.is_valid.called)

    def test_save(self):
        event = EventFactory(with_repeat=True)
        form = self.mock_out_subforms(CompositeEventForm(event))
        saved_event = form.event_form.save.return_value
        assert_equal(form.save(), saved_event)

        assert_true(form.repeat_form.save.call_args, mock.call(saved_event))
        for repeat_form in form.update_repeat_forms:
            assert_true(repeat_form.save.call_args, mock.call(saved_event))
