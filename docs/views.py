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

from __future__ import absolute_import

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext as _

from .forms import DocumentForm
from .models import Document

@login_required
def index(request):
    return render(request, 'docs/index.html', {
        'documents': Document.objects.all(),
    })


def view(request, slug):
    document = get_object_or_404(Document, slug=slug)
    if not document.public and not request.user.is_authenticated():
        return redirect_to_login(next=reverse('docs:view', args=(slug,)))
    return render(request, 'docs/view.html', {
        'document': document,
    })

@login_required
def create(request):
    return edit_form(request, None, reverse('docs:index'))

@login_required
def edit(request, slug):
    instance = get_object_or_404(Document, slug=slug)
    return edit_form(request, instance, reverse('docs:view', args=(slug,)))

def edit_form(request, instance, return_url):
    return_url = request.GET.get('return_url', return_url)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(return_url)
        if instance and 'delete' in request.POST:
            instance.delete()
            return redirect('docs:index')
        form = DocumentForm(request.user, data=request.POST,
                            instance=instance)
        if form.is_valid():
            document = form.save()
            return redirect('docs:view', document.slug)
    else:
        form = DocumentForm(request.user, instance=instance)

    if not instance:
        title = _('Create New Document')
        submit_text = _('Create')
        enable_delete = False
    else:
        title = _('Edit Document')
        submit_text = _('Update')
        enable_delete = True

    return render(request, "docs/edit.html", {
        'form': form,
        'title': title,
        'submit_text': submit_text,
        'enable_delete': enable_delete,
    })
