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

from datetime import datetime

from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
import mistune

from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    public = models.BooleanField(default=False)
    body = models.TextField()
    created = models.DateTimeField(default=datetime.now)
    author = models.ForeignKey(User)

    def __unicode__(self):
        return u'Document: {}'.format(self.title)

    def render_body(self):
        return mark_safe(mistune.markdown(self.body))
