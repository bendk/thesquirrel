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
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext as _
from django.views import generic

from .forms import DocumentForm
from .models import Document

@login_required
def index(request):
    return render(request, 'docs/index.html', {
        'documents': Document.objects.all(),
    })


def view(request, slug):
    document = get_object_or_404(Document, slug=slug)
    return render(request, 'docs/view.html', {
        'document': document,
    })

class CreateDocumentView(generic.FormView):
    form_class = DocumentForm
    template_name = "docs/edit.html"

    def title(self):
        return _('Create New Document')

    def cancel(self):
        return redirect('members')

    def form_valid(self, form):
        document = form.save()
        return redirect('docs:view', document.slug)

    def get_form_kwargs(self):
        kwargs = super(CreateDocumentView, self).get_form_kwargs()
        kwargs['author'] = self.request.user
        return kwargs

    def get_context_data(self, form):
        return {
            'title': self.title(),
            'form': form,
        }

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return self.cancel()
        return super(CreateDocumentView, self).post(request, *args, **kwargs)

class EditDocumentView(CreateDocumentView):
    def cancel(self):
        return redirect('docs:view', self.get_document().slug)

    def title(self):
        return _('Edit Document')

    def get_document(self):
        return get_object_or_404(Document, slug=self.kwargs['slug'])

    def get_form_kwargs(self):
        kwargs = super(EditDocumentView, self).get_form_kwargs()
        kwargs['instance'] = self.get_document()
        return kwargs
