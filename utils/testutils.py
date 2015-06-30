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

import functools

import mock

def reload_obj(instance):
    return instance.__class__.objects.get(pk=instance.pk)

def patch_for_test(spec, attr_name=None):
    """Use mock to patch a function for the test case.

    Use this to decorate a TestCase test or setUp method.  It will call
    TestCase.addCleanup() so that the the patch will stop at the once the test
    is complete.  It will assign the mock object used for the patch to the
    TestCase object.

    Params:
        spec: Mock spec to use
        attr_name: attribute name to set the mock object to.  By defalt we use
            last component of spec

    Example:

    class FooTest(TestCase):
        @patch_for_test('foo.bar', 'mock_bar')
        def setUp(self, mock_foo):
            # self.mock_bar is the mock object
            ...
    """
    if attr_name is None:
        attr_name = spec.split('.')[-1]
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            mock_obj = mock.Mock()
            patcher = mock.patch(spec, mock_obj)
            patcher.start()
            self.addCleanup(patcher.stop)
            setattr(self, attr_name, mock_obj)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
patch_for_test.__test__ = False
