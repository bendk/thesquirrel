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

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'thesquirrel.views.home', name='home'),
    url(r'^login/$', 'thesquirrel.views.login', name='login'),
    url(r'^logout/$', 'thesquirrel.views.logout', name='logout'),
    url(r'^editor/', include('editor.urls', 'editor')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('docs.urls', 'docs')),
)

if settings.DEV:
    urlpatterns += patterns('',
        url(r'^mediabuilder/', include('mediabuilder.urls', 'mediabuilder')),
    )
    urlpatterns += (
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )

