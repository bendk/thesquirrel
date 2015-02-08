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

from django import template
from django.core.urlresolvers import reverse

from mediabuilder import bundles

register = template.Library()

@register.simple_tag
def js_bundle(bundle_name):
    bundle = bundles.JSBundle.get_bundle(bundle_name)
    urls = [
        reverse('mediabuilder:js_source', args=(path,))
        for path in bundle.source_paths()
    ]
    return '\n'.join(
        '<script src="{}"></script>'.format(url) for url in urls
    )

@register.simple_tag
def sass_bundle(bundle_name):
    url = reverse('mediabuilder:sass_source', args=(bundle_name,))
    return '<link rel="stylesheet" type="text/css" href="{}" />'.format(url)
