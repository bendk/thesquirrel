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

from django.conf import settings

# Wrap our settings dict to provide a nicer interface and default values
class EditorConfig(object):
    # Defaults:

    # Info on how to resize images in the form of (size, width) tuples
    IMAGE_SIZES = [
        ('source', None),
        ('full', 700),
        ('small', 250),
    ]
    # Info on image styles
    IMAGE_STYLES = [
        {
            'class': 'full',
            'size': 'full',
        },
        {
            'class': 'left',
            'size': 'small',
        },
        {
            'class': 'right',
            'size': 'small',
        },
    ]

    def __getattribute__(self, name):
        try:
            return getattr(settings, 'EDITOR_CONFIG')[name]
        except (AttributeError, KeyError):
            return super(EditorConfig, self).__getattribute__(name)

config = EditorConfig()
