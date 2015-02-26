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

"""utils.test_utils.plugin -- Amara nose Plugin
"""
from __future__ import absolute_import
import os
import shutil

from django.conf import settings
from nose.plugins import Plugin

class TestPlugin(Plugin):
    name = 'thesquirrel Test Plugin'

    def options(self, parser, env=None):
        pass

    def configure(self, options, conf):
        self.enabled = True

    def begin(self):
        self.test_model_hack()
        self.override_settings()

    def finalize(self, result):
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)

    def test_model_hack(self):
        """Import a bunch of modules to ensure they get loaded.

        We need this to make django-nose create the test models
        """
        import editor.factories

    def override_settings(self):
        # disable migrations since they mess with django-nose setting up the
        # test models
        settings.MIGRATION_MODULES = dict(
            (app_name, "migrations_not_used_in_tests")
            for app_name in settings.INSTALLED_APPS
        )
        # Use a simple password hasher.  The default one is slow by design
        settings.PASSWORD_HASHERS = [
            'django.contrib.auth.hashers.MD5PasswordHasher'
        ]
        settings.MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'user-media',
                                           'test')
