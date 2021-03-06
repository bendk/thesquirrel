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
import itertools
import os
import re

from django.test import TestCase
from mock import Mock, call
import pytest

from editor.factories import *
from editor.formatting import inline
from editor.formatting import block

class OutputTest(TestCase):
    def test_append(self):
        output = block.Output()
        output.append('foo ')
        output.append('bar')
        assert output.get_string() == 'foo bar'

    def test_extend(self):
        output = block.Output()
        output.extend(['foo ', 'bar'])
        assert output.get_string() == 'foo bar'
    
    def test_add_footnote(self):
        output = block.Output()
        output.append('foo')
        assert output.append_footnote('footnote') == 1
        assert output.get_string() == (
            'foo'
            '<div class="footnotes">\n'
            '<h3>Footnotes</h3>\n'
            '<ol>\n'
            '<li id="footnote-1"><a href="#citation-1">^</a> footnote</li>\n'
            '</ol>\n'
            '</div>\n')

class InlineMarkdownTest(TestCase):
    def check_inline_render(self, source, correct_output):
        output = block.Output()
        inline.render(output, source)
        assert output.get_string() == correct_output

    # <em> and <strong> rendering
    def test_emphasis(self):
        self.check_inline_render('one *two* three', 'one <em>two</em> three')

    def test_strong(self):
        self.check_inline_render('one **two** three',
                                 'one <strong>two</strong> three')

    def test_both(self):
        self.check_inline_render('***one two***',
                                 '<strong><em>one two</em></strong>')

    def test_multi_line_em(self):
        self.check_inline_render('*one\ntwo*', '<em>one\ntwo</em>')

    def test_multi_line_strong(self):
        self.check_inline_render('**one\ntwo**', '<strong>one\ntwo</strong>')

    def test_multiple_elements(self):
        self.check_inline_render(
            '*one* **two** *three*',
            '<em>one</em> <strong>two</strong> <em>three</em>')

    # that wasn't too bad, now time to test the corner cases
    def test_nest_strong(self):
        self.check_inline_render('*one **two** three*',
                                 '<em>one <strong>two</strong> three</em>')

    def test_nest_em(self):
        self.check_inline_render('**one *two* three**',
                                 '<strong>one <em>two</em> three</strong>')

    def test_unclosed_em(self):
        # if a '*' doesn't have a closing pair, then we should not change it
        self.check_inline_render('**one*two**', '<strong>one*two</strong>')

    def test_unclosed_strong(self):
        # if a '**' doesn't have a closing pair, then we should not change it
        self.check_inline_render('*one**two*', '<em>one**two</em>')

    def test_too_many_delims(self):
        # four or more delimiters should be ignored
        self.check_inline_render('*one****two*', '<em>one****two</em>')

    def test_start_both_end_separate(self):
        # test starting with '***' then closing each separately.  Note that
        # order of the tags for "***" depends on which tag ends first
        self.check_inline_render('***one*two**',
                                 '<strong><em>one</em>two</strong>')
        self.check_inline_render('***one**two*',
                                 '<em><strong>one</strong>two</em>')

    def start_separate_end_both(self):
        self.check_inline_render('*one**two***',
                                 '<em>one<strong>two</strong></em>')
        self.check_inline_render('**one***two***',
                                 '<strong>one<em>two</em></strong>')

    def test_strong_nested_in_both(self):
        self.check_inline_render('***one**two**three***',
                                 '<em><strong>one</strong>two'
                                 '<strong>three</strong></em>')

    def test_em_nested_in_both(self):
        self.check_inline_render('***one*two*three***',
                                 '<strong><em>one</em>two'
                                 '<em>three</em></strong>')

    def test_escape_star(self):
        self.check_inline_render('\\*one\\*', '*one*')

    # link rendering
    def test_manual_link(self):
        self.check_inline_render('[Link Text](http://example.com/)',
                                 '<a href="http://example.com/">Link Text</a>')

    def test_escaping(self):
        self.check_inline_render(""" "<>& """, ' &quot;&lt;&gt;&amp; ')

    # replacing simple chars with entities
    def test_em_dash(self):
        self.check_inline_render('one--two', 'one&mdash;two')

    def test_double_quotes(self):
        self.check_inline_render('"hello"', '&ldquo;hello&rdquo;')

    def test_single_quotes(self):
        self.check_inline_render("'hello'", '&lsquo;hello&rsquo;')

    def test_single_quotes_not_used_for_apostrophe(self):
        self.check_inline_render("alice's dog's food",
                                 "alice&#x27;s dog&#x27;s food")

    def test_elipsis(self):
        self.check_inline_render("hmm...", 'hmm&hellip;')

    # everything together
    def test_mixed_markup(self):
        self.check_inline_render(
            '**[Text](http://example.com/link)**',
            '<strong><a href="http://example.com/link">Text</a></strong>')

    def test_chunked_render(self):
        output = block.Output()
        inline.chunked_render(output, ['*one', 'two*'])
        assert output.get_string() == '<em>one two</em>'

    def test_footnotes(self):
        output = Mock()
        output.append_footnote.return_value = 1
        inline.render(output, 'foo[footnote: bar]')
        assert output.method_calls == [
            call.append_footnote('bar'),
            call.append('foo'
                        '<sup id="citation-1" class="citation">'
                        '<a href="#footnote-1">[1]</a></sup>'),
        ]

class MarkdownTestCaseReader(object):
    def __init__(self, path):
        self.lines = iter(open(path).read().split('\n'))
        self.section = None

    def read_body(self):
        read_lines = []
        while True:
            line = self.lines.next()
            if line == '.':
                return read_lines
            else:
                read_lines.append(line)

    def read_comment(self):
        last_line = None
        while True:
            line = self.lines.next()
            if line == '.':
                return last_line
            elif line.startswith('#'):
                # Section start.
                self.section = line[1:].strip()
            else:
                last_line = line

@pytest.fixture
def editor_image():
    return EditorImageFactory(id=1, image_type='png')

def generate_formatting_cases():
    reader = MarkdownTestCaseReader(os.path.join(os.path.dirname(__file__),
                                                 'formatting-test-cases.txt'))
    comment = '<none>'
    while True:
        try:
            new_comment = reader.read_comment()
        except StopIteration:
            break
        if new_comment:
            comment = new_comment
        source = '\n'.join(reader.read_body())
        correct_output = '\n'.join(reader.read_body())
        yield (reader.section, comment, source, correct_output)

@pytest.mark.parametrize("section,comment,source,correct_output", generate_formatting_cases())
def check_formatting_case(editor_image, section, comment, source, correct_output):
    output = block.render(source)
    if output.endswith('\n'):
        output = output[:-1]
    if output != correct_output:
        raise AssertionError(
            '\n'.join([
                '{}: {}',
                '-- source --',
                '{}',
                '-- output--',
                '{}',
                '-- correct --',
                '{}']).format(
                    section, comment, source, output, correct_output))
