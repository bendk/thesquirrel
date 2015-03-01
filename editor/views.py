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

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from .models import EditorImage
from . import formatting

@login_required
def upload_image(request):
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'no file given'})
    else:
        image = EditorImage.objects.create_from_file(request.FILES['file'])
        return JsonResponse({'imageId': image.id})

def formatting_help(request):
    return render(request, 'editor/formatting-help.html')

@login_required
def preview(request):
    body = request.GET.get('body', '')
    return JsonResponse({'body': formatting.render(body)})
