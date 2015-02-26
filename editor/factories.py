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

from django.core.files.base import ContentFile
from factory.django import DjangoModelFactory
from PIL import Image
import factory

from django.db import models
from .fields import EditorTextField
from .models import EditorImage, EditorImageReference

class TestDocument(models.Model):
    body = EditorTextField()

class EditorImageFactory(DjangoModelFactory):
    image_type = 'png'

    class Meta:
        model = EditorImage

def make_image_file(size=(1000, 1000), image_type='png'):
    fp = ContentFile('', 'image.' + image_type)
    Image.new('RGB', size).save(fp, image_type)
    fp.seek(0)
    return fp

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

__all__ = [
    name for name, value in globals().items()
    if isinstance(value, type) and issubclass(value, factory.Factory)
]
__all__.extend([
    'make_image_file',
])
