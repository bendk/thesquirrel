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
from ..forms import EventForm

class EventFormTest(TestCase):
    def test_start_date_must_be_after_end_date(self):
        user = UserFactory()
        form = EventForm(data={
            'title': 'test-title',
            'body': 'test-body',
            'date': '1/1/2015',
            'start_time': '18:30',
            'end_time': '16:30',
        })
        assert_false(form.is_valid())

    def test_until_required_for_repeat(self):
        form = EventForm(data={
            'title': 'test-title',
            'body': 'test-body',
            'date': '1/1/2015',
            'start_time': '18:30',
            'end_time': '19:30',
            'repeat_type': '1M',
            'repeat_th': '1',
            'repeat_fr': '1',
        })
        assert_false(form.is_valid())

    def test_one_weekday_required_for_repeat(self):
        form = EventForm(data={
            'title': 'test-title',
            'body': 'test-body',
            'date': '1/1/2015',
            'start_time': '18:30',
            'end_time': '19:30',
            'repeat_until': '2/1/2015',
            'repeat_type': '1M',
        })
        assert_false(form.is_valid())

    def test_create_dates(self):
        user = UserFactory()
        form = EventForm(data={
            'title': 'test-title',
            'body': 'test-body',
            'date': '1/1/2015',
            'start_time': '18:30',
            'end_time': '19:30',
            'repeat_type': '1M',
            'repeat_until': '2/1/2015',
            'repeat_th': '1',
            'repeat_fr': '1',
        })
        assert_true(form.is_valid())
        event = form.save(user)
        assert_items_equal([d.date for d in event.date_set.all()],
                           [date(2015, 1, 1), date(2015, 1, 2)])

    def test_update(self):
        event = EventFactory()
        user = UserFactory()
        form = EventForm(instance=event, data={
            'title': 'test-title',
            'body': 'test-body',
            'date': '1/1/2015',
            'start_time': '18:30',
            'end_time': '19:30',
        })
        assert_true(form.is_valid())
        saved_event = form.save(user)
        assert_equal(saved_event.id, event.id)
        assert_equal(event.title, 'test-title')

    def test_update_with_exsting_dates(self):
        event = EventFactory(date=date(2015, 1, 2),
                             repeat_type='1M',
                             repeat_until=date(2015, 2, 1),
                             repeat_fr=True)
        event.update_dates()
        user = UserFactory()
        form = EventForm(instance=event, data={
            'title': 'test-title',
            'body': 'test-body',
            'date': '1/1/2015',
            'start_time': '18:30',
            'end_time': '19:30',
        })
        assert_true(form.is_valid())
        saved_event = form.save(user)
        assert_equal(saved_event.id, event.id)
        assert_equals([d.date for d in event.date_set.all()],
                      [date(2015, 1, 1)])
