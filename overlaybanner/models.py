# thesquirrel.org
#
# Copyright (C) 2016 Flying Squirrel Community Space
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

from django.db import models
from django.db import transaction

class OverlayBanner(models.Model):
    name = models.CharField(max_length=100)
    html = models.TextField()
    active = models.BooleanField(default=False)

    @classmethod
    def get_active(cls):
        try:
            return cls.objects.filter(active=True)[0]
        except IndexError:
            return None

    def __unicode__(self):
        return self.name

    def activate(self):
        with transaction.atomic():
            self.active = True
            self.save()
            OverlayBanner.objects.exclude(id=self.id).update(active=False)
