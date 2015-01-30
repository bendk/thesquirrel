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

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import sass
import slimit

import mediabundles

SASS_BUNDLES = getattr(settings, 'SASS_BUNDLES', {})
JS_BUNDLES = getattr(settings, 'JS_BUNDLES', {})

class Command(BaseCommand):
    help = 'Build media bundles'

    def handle(self, *args, **options):
        self.ensure_static_dir()
        for dest, bundle in SASS_BUNDLES.items():
            self.build_sass_bundle(dest, bundle)
        for dest, bundle in JS_BUNDLES.items():
            self.build_js_bundle(dest, bundle)

    def ensure_static_dir(self):
        app_dir = os.path.dirname(mediabundles.__file__)
        static_dir = os.path.join(app_dir, 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        elif not os.path.isdir(static_dir):
            raise CommandError("{} exists but is not a directory".format(
                static_dir))


    def source_path(self, source):
        return os.path.join(settings.BASE_DIR, source)

    def writeout(self, dest, content):
        app_dir = os.path.dirname(mediabundles.__file__)
        dest_path = os.path.join(app_dir, 'static', dest)
        with open(dest_path, 'w') as f:
            f.write(content)

    def build_sass_bundle(self, dest, bundle):
        self.stdout.write("Building {}\n".format(dest))
        source_path = os.path.join(settings.BASE_DIR, bundle['source'])
        content = sass.compile(
            filename=source_path,
            output_style='compressed',
            include_paths=bundle.get('include_paths', [])
        )
        self.writeout(dest, content)

    def build_js_bundle(self, dest, bundle):
        self.stdout.write("Building {}\n".format(dest))
        js_source = []
        for source in bundle['sources']:
            for path in glob.glob(self.source_path(source)):
                js_source.append(open(path).read())
        content = slimit.minify(''.join(js_source), mangle=True,
                                mangle_toplevel=False)
        self.writeout(dest, content)
