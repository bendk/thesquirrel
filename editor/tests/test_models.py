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
from datetime import timedelta
import os

from django.conf import settings
from django.test import TestCase
from django.utils import safestring
from django.utils.timezone import now
from PIL import Image

from ..models import EditorImage, EditorImageReference
from ..factories import *

class EditorImageTest(TestCase):
    def check_image_file(self, path, size):
        path = os.path.join(settings.MEDIA_ROOT, path)
        assert os.path.exists(path)
        image = Image.open(path)
        assert image.size == size

    def check_image_file_deleted(self, path):
        path = os.path.join(settings.MEDIA_ROOT, path)
        assert not os.path.exists(path)

    def test_image_creation(self):
        image = EditorImage.objects.create_from_file(
            make_image_file((1400, 1000), 'png'))
        # source image should be the size of the input image
        self.check_image_file('source/{}.png'.format(image.id), (1400, 1000))
        # full image is resized to 700px width max
        self.check_image_file('full/{}.png'.format(image.id), (700, 500))
        # small image is resized to 250px width max
        self.check_image_file('small/{}.png'.format(image.id), (250, 179))

    def test_delete_object_removes_file(self):
        image = EditorImage.objects.create_from_file(make_image_file())
        old_id = image.id
        image.delete()
        # source image should be the size of the input image
        self.check_image_file_deleted('source/{}.png'.format(old_id))
        # full image is resized to 700px width max
        self.check_image_file_deleted('full/{}.png'.format(old_id))
        # small image is resized to 250px width max
        self.check_image_file_deleted('small/{}.png'.format(old_id))

    def test_delete_unused(self):
        # #1 and #2 are used
        image1 = EditorImageFactory()
        image2 = EditorImageFactory()
        # #3 is not used, but it was recently touched
        image3 = EditorImageFactory(mtime=now()-timedelta(days=13))
        # #3 is not used, and not recently touched
        image4 = EditorImageFactory(mtime=now()-timedelta(days=15))
        image4_id = image4.id
        doc1 = MockDocumentFactory(references=[image1, image2])
        doc2 = MockDocumentFactory(references=[image1])
        EditorImage.delete_unused()
        assert set(EditorImage.objects.all()) == set([image1, image2, image3])

class EditorTextTest(TestCase):
    def check_image_references(self, doc, correct_images):
        qs = (EditorImageReference.objects
              .for_content_object(doc)
              .select_related('image'))
        assert set(ref.image for ref in qs) == set(correct_images)

    def test_create_references(self):
        images = [EditorImageFactory(id=i) for i in range(1, 5)]
        body_lines = [
            # make a couple lines with references to images
            '#image1-full',
            '#image2-left',
            '#image2-right',
            # these lines aren't valid references
            '  #image3-full',
            '# image3-full',
            '#imagethree-full',
            '#image3',
            '# header',
            'text #image3-left',
            '#image3',
        ]
        doc = MockDocumentFactory(body='\n'.join(body_lines))
        self.check_image_references(doc, images[:2])

    def test_update_references(self):
        # at first the document references images #1 and #2
        images = [EditorImageFactory(id=i) for i in range(1, 5)]
        doc = MockDocumentFactory(body='#image1-full\n#image2-full')
        # after an update it references #2 and #3
        doc = MockDocumentFactory(body='#image3-full\n#image2-full')
        # check the references
        self.check_image_references(doc, images[1:3])

    def test_update_mtimes(self):
        # at first the document references images #1 and #2
        before = now() - timedelta(days=7)
        images = [
            EditorImageFactory(id=i, mtime=before) for i in range(1, 5)
        ]
        doc = MockDocumentFactory(body='#image1-full\n#image2-full')
        # after an update it references #2 and #3
        doc = MockDocumentFactory(body='#image3-full\n#image2-full')
        # all images should have their mtimes updated
        assert set(EditorImage.objects.filter(mtime__gt=before)) == set(
            images[:3])

    def test_remove_references_on_delete(self):
        # at first the document references images #1 and #2
        images = [EditorImageFactory(id=i) for i in range(1, 5)]
        doc = MockDocumentFactory(body='#image1-full\n#image2-full')
        doc.delete()
        # check the references
        self.check_image_references(doc, [])

    def test_render_fieldname(self):
        # at first the document references images #1 and #2
        doc = MockDocumentFactory(body='# header')
        assert doc.render_body() == '<h2>header</h2>\n'
        assert isinstance(doc.render_body(), safestring.SafeText)
