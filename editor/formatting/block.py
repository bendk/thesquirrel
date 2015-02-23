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

"""editor.formatting.render -- Markdown-style formatting """

from __future__ import absolute_import
import collections
import re

from . import inline

# The first step of the processes is lexing.  We split the input string into a
# list of tokens -- one per line.
class Token(object):
    # rule that matches the input line for this token
    rule = NotImplemented

    def __init__(self, match):
        pass

class Heading(Token):
    rule = re.compile(r'#(?!#)(.*)$')
    def __init__(self, match):
        self.text = match.group(1).strip()

class SubHeading(Token):
    rule = re.compile(r'##(?!#)(.*)$')
    def __init__(self, match):
        self.text = match.group(1).strip()

class Quote(Token):
    rule = re.compile(r'>+(.*)$')
    def __init__(self, match):
        self.text = match.group(1).strip()

    def is_empty(self):
        return not self.text

class ListItem(Token):
    rule = re.compile(r'( *)[*-](.*)$')
    open_tag = '<ul>'
    close_tag = '</ul>'
    def __init__(self, match):
        self.leading = len(match.group(1))
        self.text = match.group(2).strip()

class OrderedListItem(ListItem):
    rule = re.compile(r'( *)\d+\.(.*)$')
    open_tag = '<ol>'
    close_tag = '</ol>'

class EmptyLine(Token):
    rule = re.compile(r'\s*$')

class Text(Token):
    # this has the lowest precedence, so match anything
    rule = re.compile(r'( *)(.*)$')
    def __init__(self, match):
        self.can_continue_list = bool(match.group(1))
        self.text = match.group(2).rstrip()

class EOS(object):
    """Signals the end of the token stream."""

class Lexer(object):
    """Transforms an input string into a stream of tokens

    Use next_token to get the next_token token and pop_next() to move foward
    """

    # token in order of matching precedence
    token_classes = [
        Heading,
        SubHeading,
        Quote,
        ListItem,
        OrderedListItem,
        EmptyLine,
        Text,
    ]

    def __init__(self, input_string):
        self.lines = input_string.split('\n')
        self.pos = 0
        self.calc_next()

    def make_token(self, line):
        for token_class in self.token_classes:
            match = token_class.rule.match(line)
            if match:
                return token_class(match)
        raise AssertionError("Can't match {}".format(line))

    def calc_next(self):
        try:
            self.next_token = self.make_token(self.lines[self.pos])
        except IndexError:
            self.next_token = EOS()

    def pop_next(self):
        popping = self.next_token
        self.pos += 1
        self.calc_next()
        return popping

class Renderer(object):
    """Renderers a stream of tokens."""

    def __init__(self):
        # map token classes to a methed to render that token when it's next
        self.render_map = dict(
            (token_class, self.get_render_method(token_class))
            for token_class in Lexer.token_classes
        )

    def get_render_method(self, token_class):
        return getattr(self, 'render_{}'.format(
            token_class.__name__.lower()))

    def render(self, lexer):
        output = []
        while not isinstance(lexer.next_token, EOS):
            self.render_map[lexer.next_token.__class__](lexer, output)
        return ''.join(output)

    def append_text(self, lexer, output):
        """Utility method to:
             - Pop the next token
             - Render token.text using our InlineRenderer
             - Append that text to output
        """
        output.append(inline.render(lexer.pop_next().text))

    def continue_text(self, lexer, output):
        """Utility method to do whan append_text does, but
        outputing a space beforehand.
        """
        output.append(' ')
        output.append(inline.render(lexer.pop_next().text))

    def render_heading(self, lexer, output):
        output.append('<h2>')
        self.append_text(lexer, output)
        while isinstance(lexer.next_token, Heading):
            self.continue_text(lexer, output)
        output.append('</h2>\n')

    def render_subheading(self, lexer, output):
        output.append('<h3>')
        self.append_text(lexer, output)
        while isinstance(lexer.next_token, SubHeading):
            self.continue_text(lexer, output)
        output.append('</h3>\n')

    def render_quote(self, lexer, output):
        # skip over any blank lines
        while (isinstance(lexer.next_token, Quote) and
               lexer.next_token.is_empty()):
            lexer.pop_next()
        # check for the corner case of no quote at all
        if not isinstance(lexer.next_token, Quote):
            output.append('<blockquote></blockquote>')
            return
        output.append('<blockquote>\n<p>')

        while True:
            # write out consecutive lines with content
            self.append_text(lexer, output)
            while (isinstance(lexer.next_token, Quote) and
                   not lexer.next_token.is_empty()):
                self.continue_text(lexer, output)
            # skip over any blank lines
            while (isinstance(lexer.next_token, Quote) and
                   lexer.next_token.is_empty()):
                lexer.pop_next()
            if isinstance(lexer.next_token, Quote):
                # if there is more, start a new <p>
                output.append('</p>\n<p>')
            else:
                # if not, break out
                break
        output.append('</p>\n</blockquote>\n')

    def render_text(self, lexer, output):
        output.append('<p>')
        self.append_text(lexer, output)
        while isinstance(lexer.next_token, Text):
            self.continue_text(lexer, output)
        output.append('</p>\n')

    def render_listitem(self, lexer, output):
        output.append('<ul>\n')
        self.render_list_items(lexer, output)
        output.append('</ul>\n')

    def render_orderedlistitem(self, lexer, output):
        output.append('<ol>\n')
        self.render_list_items(lexer, output)
        output.append('</ol>\n')

    def render_list_items(self, lexer, output):
        start_token = lexer.next_token
        while isinstance(lexer.next_token, ListItem):
            next_token = lexer.next_token
            # check if the next item is the same as the first.  Note that we
            # need to compare __class__ directly to avoid mixing ordered and
            # unordered list items
            if (next_token.__class__ == start_token.__class__ and
                next_token.leading == start_token.leading):
                output.append('<li>')
                self.append_text(lexer, output)
                while (isinstance(lexer.next_token, Text) and
                       lexer.next_token.can_continue_list):
                    self.continue_text(lexer, output)
                output.append('</li>\n')
            elif next_token.leading > start_token.leading:
                # more leading space, start a nested list
                nester = lexer.next_token
                output.extend(('<li>', nester.open_tag, '\n'))
                self.render_list_items(lexer, output)
                output.extend((nester.close_tag, '</li>\n'))
            else:
                break

    def render_emptyline(self, lexer, output):
        lexer.pop_next()

_renderer = Renderer()
def render(input_string):
    lexer = Lexer(input_string)
    return _renderer.render(lexer)
