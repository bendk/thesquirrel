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

import os

from django.conf import settings

# Wrap our settings dict to provide a nicer interface and default values
class MediaBuilderConfig(object):
    # defaults
    BUNDLE_MEDIA = False
    DOWNLOADS = {}
    JS_BUNDLES = {}
    CSS_BUNDLES = {}
    COPY_TO_STATIC = {}

    def __getattribute__(self, name):
        try:
            return getattr(settings, 'MEDIA_BUILDER', {})[name]
        except KeyError:
            return super(MediaBuilderConfig, self).__getattribute__(name)

config = MediaBuilderConfig()

app_root_path = os.path.dirname(__file__)

def path(*components):
    """Get a path to a file inside the mediabuilder app directory."""
    return os.path.join(app_root_path, *components)

__all__ = ['path', 'config']
