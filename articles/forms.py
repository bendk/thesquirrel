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

from django import forms
from django.utils.translation import gettext as _

from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ( 'title', 'body', )
        labels = {
            'title': '',
            'body': '',
        }

    def __init__(self, author, *args, **kwargs):
        self.author = author
        super(ArticleForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        article = super(ArticleForm, self).save(commit=False)
        article.author = self.author
        if commit:
            article.save()
        return article
