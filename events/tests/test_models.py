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
from nose.tools import *
import pytz

from ..factories import *
from ..models import Event, EventRepeat, EventDate

class TestModels(TestCase):
    def check_dates(self, event, correct_dates):
        event.update_dates()
        assert_items_equal([d.date for d in event.date_set.all()],
                           correct_dates)

    def test_create_dates_no_repeat(self):
        event = EventFactory(date=date(2015, 1, 1))
        self.check_dates(event, [date(2015, 1, 1)])

    def test_create_dates_with_repeat(self):
        event = EventFactory(date=date(2015, 1, 1))
        EventRepeat.objects.create(event=event, type='2W', th=True,
                                   until=date(2015, 2, 1))
        self.check_dates(event, [
            date(2015, 1, 1),
            date(2015, 1, 15),
            date(2015, 1, 29),
        ])

    def test_update_dates(self):
        event = EventFactory(date=date(2015, 1, 1))
        # make an extra event date -- it should be deleted in update_dates()
        EventDate.objects.create(event=event, date=date(2015, 1, 2))
        self.check_dates(event, [date(2015, 1, 1)])
