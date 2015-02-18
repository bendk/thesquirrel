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

from django.conf.urls import patterns, include, url
from docs import views

urlpatterns = patterns('docs.views',
    url(r'^$', 'index', name='index'),
    url(r'^create/$', views.CreateDocumentView.as_view(), name='create'),
    url(r'^(?P<slug>[-\w]+)/$', 'view', name='view'),
    url(r'^(?P<slug>[-\w]+)/edit/$', views.EditDocumentView.as_view(), name='edit'),
)

