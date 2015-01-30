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
import json
import shutil
import tarfile
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import requests

import weblibs

class Sources(object):
    """Manage the sources.json file

    We use this file to tell where libraries were downloaded from, so we don't
    re-download things
    """
    def __init__(self, downloads_dir):
        self.path = os.path.join(downloads_dir, 'sources.json')
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

class Command(BaseCommand):
    help = 'Download web libraries to weblibs/downloads'

    def handle(self, *args, **options):
        self.ensure_dir_exists(self.downloads_dir())
        self.sources = Sources(self.downloads_dir())
        for dest, url in settings.WEB_LIBRARIES.items():
            if self.sources.needs_download(dest, url):
                self.download_library(dest, url)
                self.sources.remember_download(dest, url)

    def downloads_dir(self):
        app_dir = os.path.dirname(weblibs.__file__)
        return os.path.join(app_dir, 'downloads')

    def ensure_dir_exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        elif not os.path.isdir(path):
            raise CommandError("{} exists but it's not a directory".format(
                path))

    def download_library(self, dest, url):
        dest_path = os.path.join(self.downloads_dir(), dest)
        self.clearout_dest_path(dest_path)
        self.stdout.write("* {}".format(url))
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
            # most tarballs put all their files inside a directory.  Move
            # these files to dest_path
            child_dir = os.path.join(dest_path, os.listdir(dest_path)[0])
            for name in os.listdir(child_dir):
                shutil.move(os.path.join(child_dir, name),
                            os.path.join(dest_path, name))
            os.rmdir(child_dir)
