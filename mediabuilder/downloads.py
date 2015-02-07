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

import requests

import mediabuilder

class Sources(object):
    """Manage the sources.json file

    We use this file to tell where libraries were downloaded from so we don't
    re-download things
    """
    def __init__(self):
        self.path = mediabuilder.path('downloads', 'sources.json')
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

class Download(object):
    sources = None # lazily created

    @staticmethod
    def all_downloads():
        return [
            Download(name, url)
            for name, url in mediabuilder.config.DOWNLOADS.items()
        ]

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.dest_path = mediabuilder.path('downloads', self.name)
        if self.__class__.sources is None:
            self.__class__.sources = Sources()

    def needs_download(self):
        return self.sources.needs_download(self.name, self.url)

    def download(self):
        self.clearout_dest_path()
        response = requests.get(self.url)
        response.raise_for_status()
        if self.is_tarball():
            self.extract_tarball(response)
        else:
            self.write_to_file(response)
        self.sources.remember_download(self.name, self.url)

    def clearout_dest_path(self):
        if os.path.exists(self.dest_path):
            if os.path.isdir(self.dest_path):
                shutil.rmtree(self.dest_path)
            else:
                os.remove(self.dest_path)

    def is_tarball(self):
        return (self.url.endswith('.tar.gz')
                or self.url.endswith('.tar.bz2')
                or self.url.endswith('.tar'))

    def write_to_file(self, response):
        open(self.dest_path, 'w').write(response.content)

    def extract_tarball(self, response):
        stream = StringIO(response.content)
        if self.url.endswith('.tar.gz'):
            mode = 'r:gz'
        elif self.url.endswith('.tar.bz2'):
            mode = 'r:bz2'
        else:
            mode = 'r'
        tar = tarfile.open(mode=mode, fileobj=stream)
        tar.extractall(self.dest_path)
        tar.close()
        if len(os.listdir(self.dest_path)) == 1:
            # Most tarballs put all their files inside a directory.  Move
            # these files to dest_path, effectively renaming the directory to
            # our name.
            tarbal_dirname = os.listdir(self.dest_path)[0]
            child_dir = os.path.join(self.dest_path, tarbal_dirname)
            for name in os.listdir(child_dir):
                shutil.move(os.path.join(child_dir, name),
                            os.path.join(self.dest_path, name))
            os.rmdir(child_dir)
