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

import collections
from datetime import timedelta
import os

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from PIL import Image

from .formatting.utils import find_images

ImageFileInfo = collections.namedtuple("ImageFileInfo", "path width")

class EditorImageManager(models.Manager):
    def create_from_file(self, fp):
        pil_image = Image.open(fp)
        instance = self.create(image_type=pil_image.format.lower())
        instance.write_files(pil_image)
        return instance

class EditorImage(models.Model):
    """An image that's been uploaded into the editor.  """
    mtime = models.DateTimeField(default=timezone.now)
    image_type = models.CharField(max_length=16)

    IMAGE_RESIZE_INFO = [
        ('source', None),
        ('full', 700),
        ('small', 250),
    ]

    objects = EditorImageManager()

    def __unicode__(self):
        return 'EditorImage-{}.{}'.format(self.id, self.image_type)

    def image_files(self):
        for name, width in self.IMAGE_RESIZE_INFO:
            path = os.path.join(settings.MEDIA_ROOT, name, self.filename())
            yield ImageFileInfo(path, width)

    def filename(self):
        return '{}.{}'.format(self.id, self.image_type.lower())

    def url(self, style):
        if style in ('left', 'right'):
            directory = 'small'
        else:
            directory = 'full'
        return '{}{}/{}'.format(settings.MEDIA_URL, directory,
                                self.filename())

    def write_files(self, pil_image):
        """Write files to the user media directory """
        self._ensure_media_directories_exist()
        for image_info in self.image_files():
            self.write_resized_image(pil_image, image_info)

    def write_resized_image(self, pil_image, image_info):
        if image_info.width is None:
            pil_image.save(open(image_info.path, 'w'), self.image_type)
        else:
            scale_factor = image_info.width / float(pil_image.size[0])
            height = int(round(pil_image.size[1] * scale_factor))
            resized = pil_image.resize((image_info.width, height))
            resized.save(open(image_info.path, 'w'), self.image_type)

    def delete(self):
        for image_info in self.image_files():
            if os.path.exists(image_info.path):
                os.unlink(image_info.path)
        super(EditorImage, self).delete()

    @classmethod
    def delete_unused(cls, days_since=14):
        """Delete any unused images

        "unused" means that they are not referenced by any content model and
        haven't been changed in a while.
        """
        since = timezone.now() - timedelta(days=days_since)
        for obj in cls.objects.filter(references__isnull=True,
                                      mtime__lt=since):
            obj.delete()

    def _ensure_media_directories_exist(self):
        for name, width in self.IMAGE_RESIZE_INFO:
            path = os.path.join(settings.MEDIA_ROOT, name)
            if not os.path.exists(path):
                os.makedirs(path)

class EditorImageReferenceQuerySet(models.QuerySet):
    def create_for_content_object(self, content_object, image_ids):
        self.bulk_create(
            EditorImageReference(content_object=content_object,
                                 image_id=image_id)
            for image_id in image_ids
        )

    def for_content_object(self, content_object):
        return self.filter(
            content_type=ContentType.objects.get_for_model(content_object),
            object_id=content_object.pk
        )

class EditorImageReference(models.Model):
    """Tracks which images are being used by which documents.
    """
    image = models.ForeignKey(EditorImage, related_name='references')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = models.Manager.from_queryset(EditorImageReferenceQuerySet)()

    @staticmethod
    def update_for_content_object(content_object, text,
                                  just_created=False):
        new_image_ids = find_images(text)
        if just_created:
            old_image_ids = set([])
        else:
            old_image_ids = set(EditorImageReference.objects
                                .for_content_object(content_object)
                                .values_list('image_id', flat=True))
        new_image_ids = set(new_image_ids)
        # create the new references
        EditorImageReference.objects.bulk_create(
            EditorImageReference(content_object=content_object,
                                 image_id=image_id)
            for image_id in (new_image_ids - old_image_ids)
        )
        if not just_created:
            # delete the old references
            (EditorImageReference.objects
             .for_content_object(content_object)
             .filter(image_id__in=old_image_ids-new_image_ids)
             .delete())
        # update the mtimes for all images
        (EditorImage.objects
         .filter(id__in=new_image_ids.union(old_image_ids))
         .update(mtime=timezone.now()))
