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
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.utils.translation import ugettext as _

from .forms import (EventWithRepeatForm, SpaceRequestForm,
                    OngoingSpaceRequestForm)
from .models import Event, EventDate, SpaceUseRequest, OngoingSpaceUseRequest

def view(request, id):
    event = get_object_or_404(Event, id=id)
    return render(request, 'events/view.html', {
        'event': event,
    })

def make_calendar(start_date):
    qs = EventDate.objects.filter(
        date__gte=start_date,
        date__lt=start_date + relativedelta(months=1),
    ).select_related('event')
    events_by_date = defaultdict(list)
    for event_date in qs:
        events_by_date[event_date.date].append(event_date.event)

    calendar = []
    for week in Calendar().monthdatescalendar(start_date.year,
                                              start_date.month):
        week_with_events = []
        for day_date in week:
            events = events_by_date[day_date]
            events.sort(key=lambda e: e.start_time)
            week_with_events.append((day_date, events))
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
        'calendar': make_calendar(start_date),
        'start_date': start_date,
        'next_month': start_date + relativedelta(months=1),
        'prev_month': start_date - relativedelta(months=1),
        'month_name': start_date.strftime("%B %Y"),
    })

@login_required
def create(request):
    return edit_form(request, None, reverse('events:calendar'))

@login_required
def edit(request, id):
    instance = get_object_or_404(Event, id=id)
    return edit_form(request, instance, reverse('events:calendar'))

def edit_form(request, instance, return_url):
    return_url = request.GET.get('return_url', return_url)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(return_url)
        if instance and 'delete' in request.POST:
            instance.delete()
            return redirect('events:calendar')
        form = EventWithRepeatForm(data=request.POST, instance=instance)
        if form.is_valid():
            event = form.save(request.user)
            return redirect('events:view', event.id)
    else:
        form = EventWithRepeatForm(instance=instance)

    if not instance:
        title = _('Create New Event')
        submit_text = _('Create')
        enable_delete = False
    else:
        title = _('Edit Event')
        submit_text = _('Update')
        enable_delete = True

    return render(request, "events/edit.html", {
        'event_form': form.event_form,
        'repeat_form': form.repeat_form,
        'title': title,
        'submit_text': submit_text,
        'enable_delete': enable_delete,
    })

def space_request_form(request):
    return _space_request_form(request, SpaceRequestForm,
                               'events/space-request-form.html')

def ongoing_space_request_form(request):
    return _space_request_form(request, OngoingSpaceRequestForm,
                               'events/ongoing-space-request-form.html')

def _space_request_form(request, form_class, template_name):
    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(
                request, messages.INFO,
                _("Thanks for considering the squirrel for your event!  "
                  "We'll get back to you soon."))
            return redirect('home')
    else:
        form = form_class()
    return render(request, template_name, {
        'form': form,
    })

@login_required
def space_requests(request):
    requests = list(SpaceUseRequest.objects.current())
    requests.extend(OngoingSpaceUseRequest.objects.current())
    requests.sort(key=lambda r: r.sort_key())
    return render(request, "events/space-requests.html", {
        'requests': requests,
    })

def space_request(request, id):
    return _space_request(request, SpaceUseRequest, id,
                          'events/space-request.html')

def ongoing_space_request(request, id):
    return _space_request(request, OngoingSpaceUseRequest, id,
                          'events/ongoing-space-request.html')

@login_required
def _space_request(request, model, id, template_name):
    space_request = get_object_or_404(model, id=id)
    if request.method == 'POST':
        if 'approve' in request.POST:
            space_request.approve()
        elif 'deny' in request.POST:
            space_request.deny()
        return redirect('events:space-requests')

    return render(request, template_name, {
        'space_request': space_request,
    })
