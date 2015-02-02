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

from optparse import make_option
import os

from django.core.management.base import BaseCommand, CommandError

import mediabuilder
from mediabuilder import bundles, downloads

class Command(BaseCommand):
    help = 'Build app CSS/JS files'

    option_list = BaseCommand.option_list + (
        make_option('--rebuild',
            action='store_true',
            dest='rebuild',
            default=False,
            help='Redownload and rebuild all media files',
        ),
    )

    def handle(self, *args, **options):
        self.setup_directories()
        for download in downloads.Download.all_downloads():
            if options['rebuild'] or download.needs_download():
                self.stdout.write("* downloading {}\n".format(download.name))
                download.download()
        for bundle in bundles.all_bundles():
            if options['rebuild'] or bundle.needs_build():
                self.stdout.write("* building {}\n".format(bundle.name))
                bundle.build()

    def setup_directories(self):
        self.ensure_dir_exists(mediabuilder.path('downloads'))
        self.ensure_dir_exists(mediabuilder.path('static'))

    def ensure_dir_exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        elif not os.path.isdir(path):
            raise CommandError("{} exists but it's not a directory".format(
                path))
