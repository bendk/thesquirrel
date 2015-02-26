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

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .models import EditorImage

@login_required
def upload_image(request):
    if 'file' not in request.FILES:
        response_data = {
            'error': 'no file given',
        }
    else:
        image = EditorImage.objects.create_from_file(request.FILES['file'])
        response_data = {
            'imageId': image.id,
        }
    return HttpResponse(json.dumps(response_data),
                        content_type='application/json')

def formatting_help(request):
    return render(request, 'editor/formatting-help.html')
