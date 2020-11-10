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

from dateutil.rrule import MO, TU, WE, TH, FR, SA, SU
from django.test import TestCase
import pytz

from ..factories import *
from ..models import (Event, EventRepeat, EventRepeatExclude,
                      CalendarItem, SpaceUseRequest)

class UpdateCalendarItemsTest(TestCase):
    def check_update_calendar_items(self, event, correct_dates_and_times):
        event.update_calendar_items()
        db_items = [ 
            (d.date, d.start_time, d.end_time)
            for d in event.calendar_items.all()
        ]
        assert set(db_items) == set(correct_dates_and_times)

    def test_no_repeat(self):
        event = EventFactory()
        self.check_update_calendar_items(event, [
            (event.date, event.start_time, event.end_time)
        ])

    def test_single_repeat(self):
        event = EventFactory(date=date(2015, 1, 1),
                             start_time=time(8),
                             end_time=time(9))
        EventRepeat.objects.create(
            event=event, type='2W', th=True,
            start_date=date(2015, 1, 2), end_date=date(2015, 2, 1),
            start_time=time(10), end_time=time(11),
        )

        self.check_update_calendar_items(event, [
            (date(2015, 1, 1), time(8), time(9)),
            (date(2015, 1, 15), time(10), time(11)),
            (date(2015, 1, 29), time(10), time(11)),
        ])

    def test_no_duplicate_dates(self):
        # if the event and repeat share the start date, we should not create a
        # duplicate
        event = EventFactory(date=date(2015, 1, 1),
                             start_time=time(8),
                             end_time=time(9))
        EventRepeat.objects.create(
            event=event, type='2W', th=True,
            start_date=date(2015, 1, 1), end_date=date(2015, 2, 1),
            start_time=time(10), end_time=time(11),
        )

        self.check_update_calendar_items(event, [
            (date(2015, 1, 1), time(8), time(9)),
            (date(2015, 1, 15), time(10), time(11)),
            (date(2015, 1, 29), time(10), time(11)),
        ])

    def test_two_repeats(self):
        event = EventFactory(date=date(2015, 1, 1),
                             start_time=time(8),
                             end_time=time(9))
        EventRepeat.objects.create(
            event=event, type='2W', th=True,
            start_date=date(2015, 1, 2), end_date=date(2015, 2, 1),
            start_time=time(10), end_time=time(11),
        )
        EventRepeat.objects.create(
            event=event, type='2W', we=True,
            start_date=date(2015, 1, 7), end_date=date(2015, 2, 1),
            start_time=time(11), end_time=time(12),
        )

        self.check_update_calendar_items(event, [
            (date(2015, 1, 1), time(8), time(9)),
            # thursday repeat rule
            (date(2015, 1, 15), time(10), time(11)),
            (date(2015, 1, 29), time(10), time(11)),
            # wednesday repeat rule
            (date(2015, 1, 7), time(11), time(12)),
            (date(2015, 1, 21), time(11), time(12)),
        ])

    def test_many_repeats(self):
        event = EventFactory(date=date(2015, 1, 1))
        correct_calendar_items = [
            (event.date, event.start_time, event.end_time)
        ]
        for i in range(5):
            year = 2016 + i
            # creating a repeat with every day of the week set so we don't
            # have to do any fancy calculation to see whih days are hit
            EventRepeat.objects.create(
                event=event, type='W', 
                mo=True, tu=True, we=True, th=True, fr=True, sa=True, su=True,
                start_date=date(year, 1, 1), end_date=date(year, 1, 2),
                start_time=time(10), end_time=time(11),
            )
            correct_calendar_items.extend([
                (date(year, 1, 1), time(10), time(11)),
                (date(year, 1, 2), time(10), time(11)),
            ])
        self.check_update_calendar_items(event, correct_calendar_items)

    def test_exclude(self):
        event = EventFactory(
            date=date(2015, 1, 1), start_time=time(8), end_time=time(9)
        )
        EventRepeat.objects.create(
            event=event,
            type='W', th=True,
            start_date=date(2015, 1, 2), end_date=date(2015, 2, 1),
            start_time=time(10), end_time=time(11),
        )
        EventRepeatExclude.objects.create(event=event, date=date(2015, 1, 8))
        EventRepeatExclude.objects.create(event=event, date=date(2015, 1, 29))

        self.check_update_calendar_items(event, [
            (date(2015, 1, 1), time(8), time(9)),
            (date(2015, 1, 15), time(10), time(11)),
            (date(2015, 1, 22), time(10), time(11)),
        ])

    def test_delete_extra_dates(self):
        event = EventFactory()
        # make an extra event date -- it should be deleted in
        # update_calendar_items()
        CalendarItem.objects.create(
            event=event,
            date=date(2015, 1, 2),
            start_time=time(11, 30), end_time=time(12, 30),
        )
        self.check_update_calendar_items(event, [
            (event.date, event.start_time, event.end_time)
        ])

class TestSpaceUseRequestModels(TestCase):
    def test_query(self):
        SingleSpaceUseRequestFactory()
        OngoingSpaceUseRequestFactory()
        with self.assertNumQueries(1):
            types = [sr.get_type_display()
                     for sr in SpaceUseRequest.objects.all().iter_subclassses()]
        assert set(types) == set(['Single use', 'Ongoing use'])
