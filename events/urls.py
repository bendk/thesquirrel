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

urlpatterns = patterns('events.views',
    url(r'^$', 'calendar', name='calendar'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'calendar',
        name='month-calendar'),
    url(r'^create/$', 'create', name='create'),
    url(r'^(?P<id>\d+)/$', 'view', name='view'),
    url(r'^(?P<id>\d+)/edit/$', 'edit', name='edit'),
    url(r'^space-request-form/$', 'space_request_form',
        name='space-request-form'),
    url(r'^ongoing-space-request-form/$', 'ongoing_space_request_form',
        name='ongoing-space-request-form'),
    url(r'^space-requests/$', 'space_requests', name='space-requests'),
    url(r'^space-requests/(?P<id>\d+)/$', 'space_request',
        name='space-request'),
)
