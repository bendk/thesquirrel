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
from django.urls import re_path, include, path
from django.conf.urls.static import static
from django.contrib import admin

import thesquirrel.views

urlpatterns = [
    re_path(r'^$', thesquirrel.views.home, name='home'),
    re_path(r'^contact-us/$', thesquirrel.views.contact_us, name='contact-us'),
    re_path(r'^email-list-signup/$', thesquirrel.views.email_list_signup,
        name='email-list-signup'),
    re_path(r'^accounts/', include('accounts.urls')),
    re_path(r'^editor/', include('editor.urls')),
    path('admin/', admin.site.urls),
    re_path(r'^articles/', include('articles.urls')),
    re_path(r'^events/', include('events.urls')),
    re_path(r'^', include('docs.urls')),
]

if settings.DEV:
    urlpatterns += [
        re_path(r'^mediabuilder/', include('mediabuilder.urls')),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
