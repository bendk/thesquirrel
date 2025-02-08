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

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory
import factory


class UserFactory(DjangoModelFactory):
    username = factory.Sequence(lambda i: 'user-{}'.format(i))
    email = factory.Sequence(lambda i: 'user-{}@example.com'.format(i))
    password = make_password('password')

    class Meta:
        model = User

__all__ = [
    name for name, value in globals().items()
    if isinstance(value, type) and issubclass(value, factory.Factory)
]
