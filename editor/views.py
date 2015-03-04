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
from django.utils.translation import gettext as _

from . import config
from .models import EditorImage
from .formatting import block

@login_required
def upload_image(request):
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'no file given'})
    else:
        try:
            image = EditorImage.objects.create_from_file(request.FILES['file'])
        except Exception, e:
            return JsonResponse({'error': str(e)})
        return JsonResponse({'imageId': image.id})

def formatting_help(request):
    return render(request, 'editor/formatting-help.html')

class PreviewRenderer(block.Renderer):
    def render_image_extra(self, image, image_token, output):
        output.append('<ul class="adjustments">\n')
        for style in config.IMAGE_STYLES:
            output.append('<li>')
            output.append('<button ')
            if image_token.style_class == style['class']:
                output.append('class="active" ')
            output.append('data-class="{}" '.format(style['class']))
            output.append('data-url="{}" '.format(image.url(style['class'])))
            output.append('data-tag="#image-{}-{}">'.format(
                image.id, style['class']))
            output.append(style['class'])
            output.append('</button></li>')
        output.append('</ul>\n')

_preview_renderer = PreviewRenderer()
@login_required
def preview(request):
    body = request.GET.get('body', '')
    return JsonResponse({
        'body': _preview_renderer.render(body),
    })
