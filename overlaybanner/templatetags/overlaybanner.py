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

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from overlaybanner.models import OverlayBanner

register = template.Library()

@register.simple_tag()
def overlaybanner():
    banner = OverlayBanner.get_active()
    if not banner:
        return ''
    return mark_safe(
        '<div class="overlay-banner" data-id="{}">'
        '<button class="close">{} <span class="fa fa-close"></span></button>'
        '<div class="content">{}</div>'
        '</div>'.format(banner.id, _('close'), banner.html))
