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

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext as _

from .forms import EventForm
from .models import Event

@login_required
def create(request):
    return edit_form(request, None, reverse('articles:index'))

@login_required
def edit(request, id):
    instance = get_object_or_404(Event, id=id)
    return edit_form(request, instance, reverse('articles:index'))

def edit_form(request, instance, return_url):
    return_url = request.GET.get('return_url', return_url)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(return_url)
        if instance and 'delete' in request.POST:
            instance.delete()
            return redirect('articles:index')
        form = EventForm(data=request.POST, instance=instance)
        if form.is_valid():
            event = form.save(request.user)
            return redirect('events:edit', event.id)
    else:
        form = EventForm(instance=instance)

    if not instance:
        title = _('Create New Event')
        submit_text = _('Create')
        enable_delete = False
    else:
        title = _('Edit Event')
        submit_text = _('Update')
        enable_delete = True

    return render(request, "events/edit.html", {
        'form': form,
        'title': title,
        'submit_text': submit_text,
        'enable_delete': enable_delete,
    })
