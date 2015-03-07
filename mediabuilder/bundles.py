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

import glob
import os

from django.conf import settings
from django.templatetags.static import static
import sass
import slimit

import mediabuilder

class Bundle(object):
    """Base class for CSS/JS bundles."""
    settings_key = NotImplemented

    def __init__(self, name, bundle_info):
        self.name = name
        self.bundle_info = bundle_info

    @classmethod
    def settings_entry(cls):
        return getattr(mediabuilder.config, cls.settings_key, {})

    @classmethod
    def all_bundles(cls):
        return [
            cls(name, info)
            for name, info in cls.settings_entry().items()
        ]

    @classmethod
    def get_bundle(cls, name):
        info = cls.settings_entry()[name]
        return cls(name, info)

    def source_path(self, source):
        return os.path.normpath(os.path.join(settings.BASE_DIR, source))

    def source_paths(self):
        paths = []
        already_added = set()
        for source in self.bundle_info['sources']:
            glob_paths = glob.glob(self.source_path(source))
            if glob_paths:
                paths.extend(p for p in glob_paths if p not in already_added)
                already_added.update(glob_paths)
            else:
                raise ValueError("no files matching {}".format(source))
        return paths

    def dest_path(self):
        return mediabuilder.path('static', self.name)

    def static_url(self):
        return static(self.name)

    def needs_build(self):
        if not os.path.exists(self.dest_path()):
            return True
        dest_mtime = os.stat(self.dest_path()).st_mtime
        return any(os.stat(path).st_mtime > dest_mtime
                   for path in self.source_paths())

    def build(self):
        content = self.build_content()
        with open(self.dest_path(), 'w') as f:
            f.write(content)

class JSBundle(Bundle):
    settings_key = 'JS_BUNDLES'

    def build_content(self):
        js_source = [open(path).read() for path in self.source_paths()]
        return slimit.minify(''.join(js_source), mangle=True,
                             mangle_toplevel=False)

class SassBundle(Bundle):
    settings_key = 'SASS_BUNDLES'

    def sass_source(self):
        # start with some code to set $static-url inside the scss files
        source = [
            '$static-url: "{}";\n'.format(settings.STATIC_URL),
        ]
        for path in self.source_paths():
            source.append(open(path).read())
        return ''.join(source)

    def include_paths(self):
        include_paths = self.bundle_info.get('include_paths', [])
        # automatically include the directories from ant source paths
        include_paths.extend(
            set(os.path.dirname(p) for p in self.source_paths()))
        return include_paths

    def build_content(self, output_style='compressed'):
        return sass.compile(
            string=self.sass_source(),
            output_style=output_style,
            include_paths=self.include_paths(),
        )

def all_bundles():
    return JSBundle.all_bundles() + SassBundle.all_bundles()
