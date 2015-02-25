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

from cStringIO import StringIO

import factory
from factory.django import DjangoModelFactory
from PIL import Image

from django.db import models
from .fields import EditorTextField
from .models import EditorImage, EditorImageReference

class TestDocument(models.Model):
    body = EditorTextField()

class EditorImageFactory(DjangoModelFactory):
    image_type = 'png'

    class Meta:
        model = EditorImage

    @factory.post_generation
    def write_files(obj, create, extracted, **kwargs):
        if extracted:
            stream = StringIO()
            Image.new('RGB', (1400, 1000)).save(stream, obj.image_type)
            obj.write_files(stream)

class TestDocumentFactory(DjangoModelFactory):
    body = 'test-body'
    class Meta:
        model = TestDocument

    @factory.post_generation
    def references(obj, create, extracted, **kwargs):
        if extracted:
            for image in extracted:
                EditorImageReference.objects.create(
                    image=image, content_object=obj)

