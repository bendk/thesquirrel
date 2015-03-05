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

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from editor.fields import EditorTextField

class Article(models.Model):
    title = models.CharField(max_length=255)
    body = EditorTextField()
    created = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User)

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return u'Article: {}'.format(self.title)
