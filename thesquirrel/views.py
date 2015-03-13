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

from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from articles.models import Article
from docs.models import Document

def home(request):
    try:
        topstory = Article.objects.all()[0]
    except IndexError:
        topstory = None
    return render(request, 'home.html', {
        'topstory': topstory
    })

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

def email_list_signup(request):
    return render(request, 'email-list-signup.html')
