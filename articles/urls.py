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

from django.urls import include, re_path

from . import views

app_name = 'articles'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^create/$', views.create, name='create'),
    re_path(r'^(?P<id>[-\w]+)/edit/$', views.edit, name='edit'),
    re_path(r'^(?P<id>[-\w]+)/', views.view, name='view'),
]
