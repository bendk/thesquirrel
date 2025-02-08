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

app_name = 'events'
urlpatterns = [
    re_path(r'^$', views.calendar, name='calendar'),
    re_path(r'^bottomliner$', views.bottomliner, name='bottomliner'),
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.calendar,
        name='month-calendar'),
    re_path(r'^create/$', views.create, name='create'),
    re_path(r'^(?P<id>\d+)/$', views.view, name='view'),
    re_path(r'^(?P<id>\d+)/edit/$', views.edit, name='edit'),
    re_path(r'^(?P<id>\d+)/link/$', views.link_event, name='link-event'),
    re_path(r'^(?P<id>\d+)/unlink/$', views.unlink_event, name='unlink-event'),
    re_path(r'^booking/$', views.book_the_space, name='book-the-space'),
    re_path(r'^space-request-form/$', views.space_request_form,
        name='space-request-form'),
    re_path(r'^ongoing-space-request-form/$', views.ongoing_space_request_form,
        name='ongoing-space-request-form'),
    re_path(r'^space-requests/$', views.space_requests, name='space-requests'),
    re_path(r'^space-requests/complete/$', views.space_requests_complete,
        name='space-requests-complete'),
    re_path(r'^space-requests/copy-notes/$', views.space_requests_copy_notes,
        name='space-requests-copy-notes'),
    re_path(r'^space-requests/(?P<id>\d+)/$', views.space_request,
        name='space-request'),
    re_path(r'^space-requests/(?P<id>\d+)/edit$', views.edit_space_request,
        name='edit-space-request'),
    re_path(r'^space-requests/(?P<id>\d+)/lookup-others/$', views.lookup_others,
        name='lookup-others'),
]
