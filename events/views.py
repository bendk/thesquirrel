# thesquirrel.org
#
# Copyright (C) 2015 Flying Squirrel Community Space
#
# thesquirrel.org is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# thesquirrel.org is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with thesquirrel.org.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from calendar import Calendar
from collections import defaultdict
from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _

from .forms import (CompositeEventForm, SingleSpaceRequestForm,
                    OngoingSpaceRequestForm, SpaceRequestUpdateForm)
from .models import (Event, CalendarItem, SpaceUseRequest,
                     SingleSpaceUseRequest, OngoingSpaceUseRequest)
from .utils import format_time
from utils.breadcrumbs import BreadCrumb

def view(request, id):
    event = get_object_or_404(Event, id=id)
    return render(request, 'events/view.html', {
        'event': event,
        'breadcrumbs': [
            BreadCrumb(_('Calendar'), 'events:calendar'),
            BreadCrumb(event.title),
        ],
    })

def make_calendar(start_date, show_pending):
    qs = CalendarItem.objects.filter(
        date__gte=start_date,
        date__lt=start_date + relativedelta(months=1),
    ).select_related('event', 'event__space_request')
    if not show_pending:
        qs = qs.filter(
            Q(event__space_request__isnull=True) |
            Q(event__space_request__state=SpaceUseRequest.APPROVED)
        )
    date_map = defaultdict(list)
    for item in qs:
        date_map[item.date].append(item)

    calendar = []
    for week in Calendar(6).monthdatescalendar(start_date.year,
                                               start_date.month):
        week_with_events = []
        for day_date in week:
            items = date_map[day_date]
            items.sort(key=lambda item: item.start_time)
            week_with_events.append((day_date, items))
        calendar.append(week_with_events)
    return calendar

def calendar(request, year=None, month=None):
    now = timezone.now()
    if year is None:
        year = now.year
    else:
        year = int(year)
    if month is None:
        month = now.month
    else:
        month = int(month)

    start_date = date(year, month, 1)

    return render(request, 'events/calendar.html', {
        'calendar': make_calendar(start_date,
                                  request.user.is_authenticated),
        'start_date': start_date,
        'next_month': start_date + relativedelta(months=1),
        'prev_month': start_date - relativedelta(months=1),
        'month_name': start_date.strftime("%B %Y"),
        'breadcrumbs': [
            BreadCrumb(_('Calendar')),
        ],
    })

def book_the_space(request):
    return render(request, 'events/book-the-space.html')

@login_required
def create(request):
    if 'space-request' in request.GET:
        space_request = get_object_or_404(SpaceUseRequest,
                                          id=request.GET['space-request'])
        space_request = space_request.get_subclass()
        instance = Event(
            title=space_request.title,
            description=space_request.description,
            space_request=space_request,
        )
        if isinstance(space_request, SingleSpaceUseRequest):
            instance.date = space_request.date
            instance.start_time = space_request.start_time
            instance.end_time = space_request.end_time
    else:
        instance = None
    return edit_form(request, instance, reverse('events:calendar'))

@login_required
def edit(request, id):
    instance = get_object_or_404(Event, id=id)
    return edit_form(request, instance, reverse('events:calendar'))

@login_required
def link_event(request, id):
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        event.space_request = get_object_or_404(
            SpaceUseRequest, id=request.POST.get('space-request')
        )
        event.save()
        return redirect('events:view', event.id)
    query = request.GET.get('q')
    if query:
        space_requests = SpaceUseRequest.objects.filter(title__icontains=query)
    else:
        space_requests = SpaceUseRequest.objects.filter(title=event.title)
    return render(request, "events/link-event.html", {
        'event': event,
        'query': query,
        'space_requests': space_requests,
    })

@login_required
def unlink_event(request, id):
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        event.space_request = None
        event.save()
    return redirect('events:view', event.id)

def edit_form(request, instance, return_url):
    return_url = request.GET.get('return_url', return_url)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(return_url)
        if instance and 'delete' in request.POST:
            instance.delete()
            return redirect('events:calendar')
        form = CompositeEventForm(data=request.POST, event=instance)
        if form.is_valid():
            event = form.save()
            if 'space-request' in request.GET:
                return redirect('events:space-request',
                                request.GET['space-request'])
            else:
                return redirect('events:view', event.id)
    else:
        form = CompositeEventForm(event=instance)

    if not instance or not instance.pk:
        title = _('Create New Event')
        submit_text = _('Create')
        enable_delete = False
    else:
        title = _('Edit Event')
        submit_text = _('Update')
        enable_delete = True

    return render(request, "events/edit.html", {
        'event_form': form.event_form,
        'exclude_form': form.exclude_form,
        'repeat_forms': form.repeat_forms,
        'update_repeat_forms': form.update_repeat_forms,
        'title': title,
        'submit_text': submit_text,
        'enable_delete': enable_delete,
    })

def space_request_form(request):
    return _space_request_form(request, SingleSpaceRequestForm,
                               'events/space-request-form-single.html')

def ongoing_space_request_form(request):
    return _space_request_form(request, OngoingSpaceRequestForm,
                               'events/space-request-form-ongoing.html')

def _space_request_form(request, form_class, template_name):
    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            space_use_request = form.save()
            space_use_request.send_email(request)
            messages.add_message(
                request, messages.INFO,
                _("Thanks for considering the squirrel for your event!  "
                  "We will contact you in the next couple days.  If you "
                  "don't hear back from us in 3 days, please call "
                  "us at 585-205-8778.  If you have any questions "
                  "please email: flying-squirrel-events@lists.rocus.org."))
            return redirect('home')
    else:
        form = form_class()
    return render(request, template_name, {
        'form': form,
        'mode': 'create',
    })

@login_required
def space_requests(request):
    request_lists = SpaceUseRequest.get_lists()
    return render(request, "events/space-requests.html", {
        'request_lists': request_lists,
        'show_all_complete_link': True,
        'breadcrumbs': [
            BreadCrumb(_('Space Requests')),
        ],
    })

@login_required
def space_requests_complete(request):
    qs = (SpaceUseRequest.objects
          .filter(list=SpaceUseRequest.COMPLETE)
          .iter_subclassses())
    return render(request, "events/space-requests.html", {
        'request_lists': [(_('Complete'), qs)],
        'breadcrumbs': [
            BreadCrumb(_('Space Requests'), 'events:space-requests'),
            BreadCrumb(_('Complete')),
        ],
    })

@login_required
def space_requests_copy_notes(request):
    request_lists = SpaceUseRequest.get_lists()
    return render(request, "events/space-requests-copy-notes.html", {
        'request_lists': request_lists,
        'breadcrumbs': [
            BreadCrumb(_('Space Requests'), 'events:space-requests'),
            BreadCrumb(_('Copy notes')),
        ],
    })

@login_required
def space_request(request, id):
    space_request = get_object_or_404(SpaceUseRequest, id=id)

    if request.method == 'POST':
        form = SpaceRequestUpdateForm(space_request, request.user,
                                      request.POST)
        if form.is_valid():
            form.save()
            return redirect('events:space-requests')
    else:
        form = SpaceRequestUpdateForm(space_request, request.user)

    return render(request, 'events/space-request.html', {
        'space_request': space_request,
        'form': form,
        'notes': space_request.notes.all().select_related('user'),
        'breadcrumbs': [
            BreadCrumb(_('Space Requests'), 'events:space-requests'),
            BreadCrumb(space_request.title),
        ],
    })

@login_required
def lookup_others(request, id):
    space_request = get_object_or_404(SpaceUseRequest, id=id)
    other_requests = (
        SpaceUseRequest.objects.lookup_others(space_request).iter_subclassses())
    return render(request, "events/lookup-others.html", {
        'space_request': space_request,
        'other_requests': other_requests,
    })

@login_required
def edit_space_request(request, id):
    space_request = get_object_or_404(SpaceUseRequest, id=id).get_subclass()
    if isinstance(space_request, SingleSpaceUseRequest):
        form_class = SingleSpaceRequestForm
        template_name = 'events/space-request-form-single.html'
    else:
        form_class = OngoingSpaceRequestForm
        template_name = 'events/space-request-form-ongoing.html'

    if request.method == 'POST':
        form = form_class(instance=space_request, data=request.POST)
        if form.is_valid():
            space_use_request = form.save()
            return redirect('events:space-request', space_request.id)
    else:
        form = form_class(instance=space_request)
    return render(request, template_name, {
        'space_request': space_request,
        'form': form,
        'mode': 'edit',
    })

@login_required
def bottomliner(request):
    events = (Event.objects
              .filter(calendar_items__date=date.today())
              .select_related('space_request'))

    return render(request, 'events/bottomliner.html', {
        'events': events,
    })
