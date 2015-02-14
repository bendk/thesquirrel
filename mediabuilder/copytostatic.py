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

import os
import shutil

from django.conf import settings

import mediabuilder

def _directory_mtimes(path):
    """Get a dict mapping filenames to mtimes.

    For subdirectories, a child dict will be created.

    This function is useful for checking if two directories have the same
    contents.  The dicts will be different if any files are different, or any
    files have different mtimes.
    """
    rv = {}
    for filename in os.listdir(path):
        child_path = os.path.join(path, filename)
        if not os.path.isdir(child_path):
            rv[filename] = os.stat(child_path).st_mtime
        else:
            rv[filename] = _directory_mtimes(child_path)
    return rv

class CopyToStaticDirectory(object):
    """Copy directories to the static directory.

    This is usefull to copy subdirectories of our downloads to the static
    director.
    """

    def __init__(self, name):
        self.name = name
        self.source_path = mediabuilder.config.COPY_TO_STATIC[name]
        self.dest_path = mediabuilder.path('static', name)

    def needs_copy(self):
        return (not os.path.exists(self.dest_path) or
                _directory_mtimes(self.source_path) !=
                _directory_mtimes(self.dest_path))

    def copy(self):
        if os.path.exists(self.dest_path):
            shutil.rmtree(self.dest_path)
        shutil.copytree(self.source_path, self.dest_path)

def all_entries():
    return [CopyToStaticDirectory(name)
            for name in mediabuilder.config.COPY_TO_STATIC]
