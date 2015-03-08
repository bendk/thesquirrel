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

"""Define ways that we can repeat events."""

from dateutil import rrule
from django.utils.translation import ugettext_lazy as _

class WeeklyRule(object):
    def __init__(self, interval):
        self.interval = interval

    def rrule(self, weekdays, **kwargs):
        return rrule.rrule(rrule.WEEKLY, interval=self.interval,
                           byweekday=weekdays, **kwargs)

class NthWeeksOfTheMonthRule(object):
    def __init__(self, *week_numbers):
        self.week_numbers = week_numbers

    def rrule(self, weekdays, **kwargs):
        return rrule.rrule(rrule.MONTHLY,
                           byweekday=(weekday(number)
                                      for weekday in weekdays
                                      for number in self.week_numbers),
                           **kwargs)

# list of (code, label, rule) objects
repeat_rule_types = [
    ('W', 'Every Week', WeeklyRule(1)),
    ('2W', 'Every Other Week', WeeklyRule(2)),
    ('1M', 'First Week of the month', NthWeeksOfTheMonthRule(1)),
    ('2M', 'Second Week of the month', NthWeeksOfTheMonthRule(2)),
    ('3M', 'Third Week of the month', NthWeeksOfTheMonthRule(3)),
    ('4M', 'Fourth Week of the month', NthWeeksOfTheMonthRule(4)),
    ('LM', 'Last Week of the month', NthWeeksOfTheMonthRule(-1)),
    ('13M', '1st/3rd Week of the month', NthWeeksOfTheMonthRule(1, 3)),
    ('24M', '2nd/4th Week of the month', NthWeeksOfTheMonthRule(2, 4)),
]

CHOICES = [
    (code, label)
    for (code, label, rule) in repeat_rule_types
]
rule_map = dict(
    (code, rule)
    for (code, label, rule) in repeat_rule_types
)

def get_rrule(code, start, until, weekdays):
    return rule_map[code].rrule(weekdays, dtstart=start, until=until)
