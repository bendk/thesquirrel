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
from datetime import date, time, timedelta

from factory.django import DjangoModelFactory
import factory

from thesquirrel.factories import *
from .models import (Event, EventRepeat, EventRepeatExclude,
                     SingleSpaceUseRequest, OngoingSpaceUseRequest)

class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event

    title = 'test-event'
    description = 'test-event-description'
    date = date(2015, 1, 1)
    start_time = time(12, 0)
    end_time = time(14, 0)

    @factory.post_generation
    def with_repeat(obj, create, extracted, **kwargs):
        if extracted:
            EventRepeat.objects.create(
                event=obj, type='2W', th=True,
                start_date=obj.date + timedelta(days=1),
                end_date=obj.date + timedelta(days=30),
                start_time=obj.start_time,
                end_time=obj.end_time
            )

    @factory.post_generation
    def with_exclude(obj, create, extracted, **kwargs):
        if extracted:
            EventRepeatExclude.objects.create(
                event=obj, date=obj.date + timedelta(days=1),
            )

class EventRepeatFactory(DjangoModelFactory):
    class Meta:
        model = EventRepeat

    type = '2W'
    th = True
    start_date = date(2015, 1, 1)
    end_date = date(2015, 2, 1)
    start_time = time(7)
    end_time = time(8)

class SpaceUseRequestFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: 'event-request-{}'.format(n))
    description = 'my event'
    name = 'Susan B. Event Requestor'
    email = 'susan@example.com'
    squirrel_member = 'No'
    organization = 'First Wave'
    website = 'example.com'
    mission = 'To get the vote'
    phone_number = '555-555-5555'
    additional_comments = 'Extra comments'

class SingleSpaceUseRequestFactory(SpaceUseRequestFactory):
    class Meta:
        model = SingleSpaceUseRequest

    event_type = 'Speaker'
    date = date(2015, 1, 1)
    start_time = time(12, 0)
    end_time = time(13, 30)
    setup_time = '1 hour before'
    cleanup_time = '1 hour'
    event_charge = '$50'
    squirrel_donation = 'Yes the donation works for us'

class OngoingSpaceUseRequestFactory(SpaceUseRequestFactory):
    class Meta:
        model = OngoingSpaceUseRequest

    dates = 'first monday and wednesday'
    frequency = 'monthly'
    squirrel_goals = 'We will be promoting feminism'
    space_needs = 'Chairs'

__all__ = [
    name for name, value in globals().items()
    if isinstance(value, type) and issubclass(value, factory.Factory)
]
