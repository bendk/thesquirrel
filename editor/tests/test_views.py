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

from __future__ import absolute_import
import json
import os

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from nose.tools import *
from PIL import Image
import mock

from ..models import EditorImage
from ..factories import *
from thesquirrel.factories import *

class TestUploadImage(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.url = reverse('editor:upload-image')

    def test_upload_image(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.post(self.url, {
            'file': make_image_file()
        })
        assert_equal(response.status_code, 200)
        assert_equal(response['content-type'], 'application/json')
        response_data = json.loads(response.content)
        image = EditorImage.objects.get(id=response_data['imageId'])
        for path, width in image.image_files():
            assert_true(os.path.exists(path))

    def test_login_required(self):
        response = self.client.post(self.url, {
            'file': make_image_file()
        })
        assert_equal(response.status_code, 302)

class TestCopyImage(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.url = reverse('editor:copy-image')

    def test_copy_image(self):
        self.client.login(username=self.user.username, password='password')
        mock_get = mock.Mock(return_value=mock.Mock(
            status_code=200,
            content=make_image_file().read(),
        ))
        with mock.patch('requests.get', mock_get):
            response = self.client.post(self.url, {
                'url': 'http://example.com/',
            })
        assert_true(mock_get.called)
        assert_equal(mock_get.call_args, mock.call('http://example.com/'))
        assert_equal(response.status_code, 200)
        assert_equal(response['content-type'], 'application/json')
        response_data = json.loads(response.content)
        image = EditorImage.objects.get(id=response_data['imageId'])
        for path, width in image.image_files():
            assert_true(os.path.exists(path))

    def test_login_required(self):
        response = self.client.post(self.url, {
            'url': 'http://example.com/',
        })
        assert_equal(response.status_code, 302)
