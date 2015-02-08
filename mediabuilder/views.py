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

import os

from django.conf import settings
from django.http import Http404, HttpResponse

from mediabuilder import bundles

def check_source_path(bundles, path):
    """Source paths

    This method will raise Http404 if path is not a source path any of the
    bundles.
    """
    if not os.path.exists(path):
        raise Http404()
    for bundle in bundles:
        for source_path in bundle.source_paths():
            if os.path.samefile(path, source_path):
                return
    raise Http404()

def js_source(request, path):
    check_source_path(bundles.JSBundle.all_bundles(), path)
    path = os.path.join(settings.BASE_DIR, path)
    return HttpResponse(open(path).read(),
                        content_type='application/javascript')

def sass_source(request, bundle_name):
    # We can't just send the SASS source to the browser, so we build it here
    # and output it.
    bundle = bundles.SassBundle.get_bundle(bundle_name)
    return HttpResponse(bundle.build_content(), content_type='text/css')
