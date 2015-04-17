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

from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.http import is_safe_url
from django.utils.translation import ugettext as _

from . import forms
from .models import NewAccountNonce

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
            next_url = request.GET.get('next')
            if next_url and is_safe_url(next_url):
                return HttpResponseRedirect(next_url)
            else:
                return redirect("home")
    else:
        form = AuthenticationForm(request)
    return render(request, 'registration/login.html', {
        'form': form,
    })

def logout(request):
    auth.logout(request)
    return redirect("home")

@login_required
def my(request):
    if request.method == 'POST':
        form = forms.AccountForm(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save(request)
            return redirect("accounts:my")
    else:
        form = forms.AccountForm(instance=request.user)
    return render(request, 'registration/my-account.html', {
        'form': form,
    })

@login_required
def invite(request):
    if request.method == 'POST':
        form = forms.InviteMemberForm(data=request.POST)
        if form.is_valid():
            form.create_invite(request.user)
            messages.add_message(
                request, messages.INFO,
                _("An invite has been sent to {email}").format(
                    email=form.cleaned_data['email'])
            )
            return redirect("home")
    else:
        form = forms.InviteMemberForm()
    return render(request, 'registration/invite.html', {
        'form': form,
    })

def create(request, code):
    nonce = get_object_or_404(NewAccountNonce.objects.active(), code=code)
    initial = dict(email=nonce.email)
    if request.method == 'POST':
        form = forms.CreateAccountForm(initial=initial, data=request.POST)
        if form.is_valid():
            user = form.save(request)
            messages.add_message(
                request, messages.INFO,
                _("Welcome to the squirrel.org {username}!").format(
                    username=user.username)
            )
            return redirect("home")
    else:
        form = forms.CreateAccountForm(initial=initial)
    return render(request, 'registration/create.html', {
        'form': form,
    })
