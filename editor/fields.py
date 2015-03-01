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

import re

from django.db import models
from django.db.models.signals import post_save
from django.utils import safestring
from django.utils import timezone

from .models import EditorImage, EditorImageReference
from . import formatting

class EditorTextField(models.TextField):
    def contribute_to_class(self, cls, name):
        super(EditorTextField, self).contribute_to_class(cls, name)
        post_save.connect(self._on_post_save, cls)
        setattr(cls, 'render_{}'.format(name),
                lambda self: safestring.mark_safe(
                    formatting.render(getattr(self, name))))

    def _on_post_save(self, sender, instance, created, **kwargs):
        text = getattr(instance, self.attname, None)
        EditorImageReference.update_for_content_object(
            instance, text, created)
