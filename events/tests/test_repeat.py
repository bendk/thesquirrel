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
from datetime import datetime

from dateutil.rrule import MO, TU, WE, TH, FR, SA, SU
from django.test import TestCase
from nose.tools import *

from .. import repeat

class TestRepeatRules(TestCase):
    def test_weekly(self):
        rrule = repeat.get_rrule('W', datetime(2015, 1, 5),
                                 datetime(2015, 2, 1), [MO, WE])
        assert_equal(list(rrule), [
            datetime(2015, 1, 5), datetime(2015, 1, 7),
            datetime(2015, 1, 12), datetime(2015, 1, 14),
            datetime(2015, 1, 19), datetime(2015, 1, 21),
            datetime(2015, 1, 26), datetime(2015, 1, 28),
        ])

    def test_byweekly(self):
        rrule = repeat.get_rrule('2W', datetime(2015, 1, 5),
                                 datetime(2015, 2, 1), [MO, WE])
        assert_equal(list(rrule), [
            datetime(2015, 1, 5), datetime(2015, 1, 7),
            datetime(2015, 1, 19), datetime(2015, 1, 21),
        ])

    def test_first_week_of_the_month(self):
        rrule = repeat.get_rrule('1M', datetime(2015, 1, 5),
                                 datetime(2015, 3, 1), [MO, WE])
        assert_equal(list(rrule), [
            datetime(2015, 1, 5), datetime(2015, 1, 7),
            datetime(2015, 2, 2), datetime(2015, 2, 4),
        ])

    def test_second_fourth_weeks_of_the_month(self):
        rrule = repeat.get_rrule('24M', datetime(2015, 1, 12),
                                 datetime(2015, 3, 1), [MO, WE])
        assert_equal(list(rrule), [
            datetime(2015, 1, 12), datetime(2015, 1, 14),
            datetime(2015, 1, 26), datetime(2015, 1, 28),
            datetime(2015, 2, 9), datetime(2015, 2, 11),
            datetime(2015, 2, 23), datetime(2015, 2, 25),
        ])

    def test_with_time(self):
        rrule = repeat.get_rrule('1M', datetime(2015, 1, 5, 5, 30),
                                 datetime(2015, 3, 1), [MO, WE])
        assert_equal(list(rrule), [
            datetime(2015, 1, 5, 5, 30), datetime(2015, 1, 7, 5, 30),
            datetime(2015, 2, 2, 5, 30), datetime(2015, 2, 4, 5, 30),
        ])
