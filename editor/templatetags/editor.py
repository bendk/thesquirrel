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
from cgi import escape

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from ..formatting import block

register = template.Library()

@register.tag
def formattingexample(parser, token):
    nodelist = parser.parse(('endformattingexample',))
    parser.delete_first_token()
    return MarkdownExampleNode(nodelist)

class ExampleRenderer(block.Renderer):
    def render_image(self, lexer, output):
        lexer.pop_next()
        output.append('<figure class="full">\n')
        output.append('<img src="/static/editor/squirrel.jpg">\n')
        if isinstance(lexer.next_token, block.Caption):
            output.append('<figcaption>{}</figcaption>\n'.format(
                lexer.pop_next().text))
        output.append('</figure>')

def render_example(input_string):
    lexer = block.Lexer(input_string)
    return ExampleRenderer().render(lexer)

class MarkdownExampleNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        source = unicode(self.nodelist.render(context)).strip()
        return render_to_string('editor/formatting-example.html', {
            'source': mark_safe(escape(source).replace('\n', '<br>')),
            'rendered': mark_safe(render_example(source)),
        })
