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

from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import NewAccountNonce

class InviteMemberForm(forms.Form):
    email = forms.EmailField()

    def create_invite(self, user):
        return NewAccountNonce.objects.create(
            email=self.cleaned_data['email'],
            invited_by=user)

class AccountForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(),
                                required=False, label=_('Password'))
    password2 = forms.CharField(widget=forms.PasswordInput(),
                                required=False, label=_('Confirm Password'))

    def clean(self):
        data = super(AccountForm, self).clean()
        if (('password1' in data or 'password2' in data) and
            data.get('password1') != data.get('password2')):
            self.add_error('password1', _("Passwords don't match"))
        return data

    def save(self, request):
        user = super(AccountForm, self).save(commit=False)
        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])
        user.save()
        if self.cleaned_data.get('password1'):
            self.login_user(request, user.username)
        return user

    def login_user(self, request, username):
        # need to re-log the user in
        user = auth.authenticate(username=username,
                                 password=self.cleaned_data['password1'])
        auth.login(request, user)

    class Meta:
        model = User
        fields = (
            'email', 'password1', 'password2',
        )

class CreateAccountForm(AccountForm):
    def __init__(self, *args, **kwargs):
        super(CreateAccountForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['password1'].required = True
        self.fields['password2'].required = True

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password1', 'password2',
        )
