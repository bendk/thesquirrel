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
from .. import video
from ..models import EditorImage

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
    rule = re.compile(r'(>+)(.*)$')
    def __init__(self, match):
        self.count = len(match.group(1))
        self.text = match.group(2).strip()

    def is_empty(self):
        return not self.text

class ListItem(Token):
    rule = re.compile(r'( *)([*-])(.*)$')
    open_tag = '<ul>'
    close_tag = '</ul>'
    def __init__(self, match):
        self.leading = len(match.group(1))
        self.list_char = match.group(2)
        self.text = match.group(3).strip()

    def continues_list(self, other_token):
        # note that this comparison will always fail when compairing a
        # ListItem to an OrderedListItem
        return (self.list_char == other_token.list_char and
                self.leading == other_token.leading)

class OrderedListItem(ListItem):
    rule = re.compile(r'( *)\d+([\.)])(.*)$')
    open_tag = '<ol>'
    close_tag = '</ol>'

class Image(ListItem):
    rule = re.compile(r'#image-(\d+)-(\w+)\s*$')
    def __init__(self, match):
        self.image_id = match.group(1)
        self.style_class = match.group(2)

class Caption(ListItem):
    rule = re.compile(r'#caption *(.*)$')
    def __init__(self, match):
        self.text = match.group(1)

class Video(ListItem):
    rule = re.compile(r'\[ *([^\s]+) *]$')
    def __init__(self, match):
        self.url = match.group(1)

class EmptyLine(Token):
    rule = re.compile(r'\s*$')

class Text(Token):
    # this has the lowest precedence, so match anything
    rule = re.compile(r'(.*)$')
    def __init__(self, match):
        self.text = match.group(1).strip()

class EOS(object):
    """Signals the end of the token stream."""

class Lexer(object):
    """Transforms an input string into a stream of tokens

    Use next_token to get the next_token token and pop_next() to move foward
    """

    # token in order of matching precedence
    token_classes = [
        Image,
        Caption,
        Video,
        Heading,
        SubHeading,
        Quote,
        ListItem,
        OrderedListItem,
        EmptyLine,
        Text,
    ]

    def __init__(self, input_string):
        self.lines = input_string.splitlines()
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

    def render(self, input_string):
        lexer = Lexer(input_string)
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
        text_parts = [lexer.pop_next().text]
        while isinstance(lexer.next_token, Heading):
            text_parts.append(lexer.pop_next().text)
        output.extend(inline.chunked_render(text_parts))
        output.append('</h2>\n')

    def render_subheading(self, lexer, output):
        output.append('<h3>')
        self.append_text(lexer, output)
        while isinstance(lexer.next_token, SubHeading):
            self.continue_text(lexer, output)
        output.append('</h3>\n')

    def render_quote(self, lexer, output):
        nesting_level = 0
        text_parts = []
        while isinstance(lexer.next_token, Quote):
            token = lexer.pop_next()
            if token.is_empty():
                # blank line, create a paragraph
                if text_parts:
                    output.append('<p>')
                    output.extend(inline.chunked_render(text_parts))
                    output.append('</p>\n')
                    text_parts = []
                continue
            if token.count != nesting_level:
                # new nesting level
                if text_parts:
                    output.append('<p>')
                    output.extend(inline.chunked_render(text_parts))
                    output.append('</p>\n')
                    text_parts = []
                for i in xrange(token.count - nesting_level):
                    output.append('<blockquote>\n')
                for i in xrange(nesting_level - token.count):
                    output.append('</blockquote>\n')
                nesting_level = token.count
                if token.text:
                    text_parts.append(token.text)
            else:
                text_parts.append(token.text)

        # done with the list, write out text and close our tags
        if text_parts:
            output.append('<p>')
            output.extend(inline.chunked_render(text_parts))
            output.append('</p>\n')
        for i in xrange(nesting_level):
            output.append('</blockquote>\n')

    def render_text(self, lexer, output):
        output.append('<p>')
        text_parts = [lexer.pop_next().text]
        while isinstance(lexer.next_token, Text):
            text_parts.append(lexer.pop_next().text)
        output.extend(inline.chunked_render(text_parts))
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
            # check if the next item is the same as the first.  Note that we
            # need to compare __class__ directly to avoid mixing ordered and
            # unordered list items
            if lexer.next_token.continues_list(start_token):
                output.append('<li>')
                text_parts = [lexer.pop_next().text]
                while isinstance(lexer.next_token, Text):
                    text_parts.append(lexer.pop_next().text)
                output.extend(inline.chunked_render(text_parts))
                output.append('</li>\n')
            elif lexer.next_token.leading > start_token.leading:
                # more leading space, start a nested list
                nester = lexer.next_token
                output.extend(('<li>', nester.open_tag, '\n'))
                self.render_list_items(lexer, output)
                output.extend((nester.close_tag, '</li>\n'))
            else:
                break

    def render_image(self, lexer, output):
        image_token = lexer.pop_next()
        try:
            image = EditorImage.objects.get(id=image_token.image_id)
        except EditorImage.DoesNotExist:
            return
        output.append('<figure class="{}">\n'.format(image_token.style_class))
        output.append('<img src="{}">\n'.format(image.url(
            image_token.style_class)))
        if isinstance(lexer.next_token, Caption):
            output.append('<figcaption>{}</figcaption>\n'.format(
                lexer.pop_next().text))
        self.render_image_extra(image, image_token, output)
        output.append('</figure>\n')

    def render_caption(self, lexer, output):
        # We shouldn't get here since captions should be paired with images.
        # If we do, just output a <p> tag.
        output.append('<p>{}</p>\n'.format(lexer.pop_next().text))

    def render_image_extra(self, image, image_token, output):
        pass

    def render_video(self, lexer, output):
        output.append(video.render_video_for_url(lexer.pop_next().url))

    def render_emptyline(self, lexer, output):
        lexer.pop_next()

_renderer = Renderer()
def render(input_string):
    return _renderer.render(input_string)
