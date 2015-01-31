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

from cStringIO import StringIO
import glob
import json
import shutil
import tarfile
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import requests
import sass
import slimit

import mediabuilder

conf = getattr(settings, 'MEDIA_BUILDER', {})
DOWNLOADS = conf.get('DOWNLOADS', {})
SASS_BUNDLES = conf.get('SASS_BUNDLES', {})
JS_BUNDLES = conf.get('JS_BUNDLES', {})

def mediabuilder_path(*components):
    app_dir = os.path.dirname(mediabuilder.__file__)
    return os.path.join(app_dir, *components)

class Sources(object):
    """Manage the sources.json file

    We use this file to tell where libraries were downloaded from so we don't
    re-download things
    """
    def __init__(self):
        self.path = mediabuilder_path('downloads', 'sources.json')
        if os.path.exists(self.path):
            self.entries = json.load(open(self.path))
        else:
            self.entries = {}

    def needs_download(self, dest, url):
        return self.entries.get(dest) != url

    def remember_download(self, dest, url):
        self.entries[dest] = url
        with open(self.path, 'w') as f:
            json.dump(self.entries, f,
                      sort_keys=True, indent=4,
                      separators=(',', ': '))

class Downloader(object):
    """Download web libraries."""
    def __init__(self, stdout):
        self.stdout = stdout

    def run(self):
        sources = Sources()
        for dest, url in DOWNLOADS.items():
            if sources.needs_download(dest, url):
                self.download_library(dest, url)
                sources.remember_download(dest, url)

    def download_library(self, dest, url):
        dest_path = mediabuilder_path('downloads', dest)
        self.clearout_dest_path(dest_path)
        self.stdout.write("* downloading {}".format(url))
        response = requests.get(url)
        response.raise_for_status()
        if self.is_tarball(url):
            self.extract_tarball(url, dest_path, response)
        else:
            self.write_to_file(url, dest_path, response)

    def clearout_dest_path(self, dest_path):
        if os.path.exists(dest_path):
            if os.path.isdir(dest_path):
                shutil.rmtree(dest_path)
            else:
                os.remove(dest_path)

    def write_to_file(self, url, dest_path, response):
        open(dest_path, 'w').write(response.content)

    def is_tarball(self, url):
        return (url.endswith('.tar.gz')
                or url.endswith('.tar.bz2')
                or url.endswith('.tar'))

    def extract_tarball(self, url, dest_path, response):
        stream = StringIO(response.content)
        if url.endswith('.tar.gz'):
            mode = 'r:gz'
        elif url.endswith('.tar.bz2'):
            mode = 'r:bz2'
        else:
            mode = 'r'
        tar = tarfile.open(mode=mode, fileobj=stream)
        tar.extractall(dest_path)
        tar.close()
        if len(os.listdir(dest_path)) == 1:
            # Most tarballs put all their files inside a directory.  Move
            # these files to dest_path, effectively renaming the directory to
            # our name.
            child_dir = os.path.join(dest_path, os.listdir(dest_path)[0])
            for name in os.listdir(child_dir):
                shutil.move(os.path.join(child_dir, name),
                            os.path.join(dest_path, name))
            os.rmdir(child_dir)

class Bundler(object):
    """Combine/compile/compress JS and CSS files."""
    def __init__(self, stdout):
        self.stdout = stdout

    def run(self):
        for dest, bundle in SASS_BUNDLES.items():
            self.build_sass_bundle(dest, bundle)
        for dest, bundle in JS_BUNDLES.items():
            self.build_js_bundle(dest, bundle)

    def source_path(self, source):
        return os.path.join(settings.BASE_DIR, source)

    def writeout(self, dest, content):
        dest_path = mediabuilder_path('static', dest)
        with open(dest_path, 'w') as f:
            f.write(content)

    def build_sass_bundle(self, dest, bundle):
        self.stdout.write("* building {}\n".format(dest))
        content = sass.compile(
            filename=self.source_path(bundle['source']),
            output_style='compressed',
            include_paths=bundle.get('include_paths', [])
        )
        self.writeout(dest, content)

    def build_js_bundle(self, dest, bundle):
        self.stdout.write("* building {}\n".format(dest))
        js_source = []
        for source in bundle['sources']:
            for path in glob.glob(self.source_path(source)):
                js_source.append(open(path).read())
        content = slimit.minify(''.join(js_source), mangle=True,
                                mangle_toplevel=False)
        self.writeout(dest, content)

class Command(BaseCommand):
    help = 'Build app CSS/JS files'

    def handle(self, *args, **options):
        self.setup_directories()
        Downloader(self.stdout).run()
        Bundler(self.stdout).run()

    def setup_directories(self):
        self.ensure_dir_exists(mediabuilder_path('downloads'))
        self.ensure_dir_exists(mediabuilder_path('static'))

    def ensure_dir_exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        elif not os.path.isdir(path):
            raise CommandError("{} exists but it's not a directory".format(
                path))
