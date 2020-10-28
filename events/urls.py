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

from django.conf.urls import include, url

from . import views

app_name = 'events'
urlpatterns = [
    url(r'^$', views.calendar, name='calendar'),
    url(r'^bottomliner$', views.bottomliner, name='bottomliner'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.calendar,
        name='month-calendar'),
    url(r'^create/$', views.create, name='create'),
    url(r'^(?P<id>\d+)/$', views.view, name='view'),
    url(r'^(?P<id>\d+)/edit/$', views.edit, name='edit'),
    url(r'^(?P<id>\d+)/link/$', views.link_event, name='link-event'),
    url(r'^(?P<id>\d+)/unlink/$', views.unlink_event, name='unlink-event'),
    url(r'^booking/$', views.book_the_space, name='book-the-space'),
    url(r'^space-request-form/$', views.space_request_form,
        name='space-request-form'),
    url(r'^ongoing-space-request-form/$', views.ongoing_space_request_form,
        name='ongoing-space-request-form'),
    url(r'^space-requests/$', views.space_requests, name='space-requests'),
    url(r'^space-requests/complete/$', views.space_requests_complete,
        name='space-requests-complete'),
    url(r'^space-requests/copy-notes/$', views.space_requests_copy_notes,
        name='space-requests-copy-notes'),
    url(r'^space-requests/(?P<id>\d+)/$', views.space_request,
        name='space-request'),
    url(r'^space-requests/(?P<id>\d+)/edit$', views.edit_space_request,
        name='edit-space-request'),
    url(r'^space-requests/(?P<id>\d+)/lookup-others/$', views.lookup_others,
        name='lookup-others'),
]
