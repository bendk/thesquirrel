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

from __future__ import absolute_import
from datetime import timedelta
from random import SystemRandom
import string

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.urls import reverse

random = SystemRandom()
CODE_ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits + '-_'
# 64 characters == 6 bits
CODE_LENGTH = 12
# 6 bits * 12 is over 64 bits of data, which should be enough for a nonce

def make_code():
    return ''.join(random.sample(CODE_ALPHABET, CODE_LENGTH))

class NewAccountNonceManager(models.Manager):
    def active(self):
        return self.filter(created__gte=timezone.now() - timedelta(days=14))

    def expired(self):
        return self.filter(created__lt=timezone.now() - timedelta(days=14))

class NewAccountNonce(models.Model):
    code = models.CharField(max_length=CODE_LENGTH, default=make_code)
    email = models.CharField(max_length=255)
    invited_by = models.ForeignKey(User, models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    objects = NewAccountNonceManager()

    def create_url(self):
        return reverse("accounts:create", args=(self.code,))

    def send_email(self, request):
        message = render_to_string('registration/invite-email.txt', {
            'create_url': request.build_absolute_uri(self.create_url()),
        })
        send_mail('TheSquirrel.org account invitation', message,
                  settings.DEFAULT_FROM_EMAIL,
                  [self.email], fail_silently=False)

