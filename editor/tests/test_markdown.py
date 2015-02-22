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

from django.test import TestCase
from nose.tools import *

from editor.markdown import inline
from editor.markdown import render

class InlineMarkdownTest(TestCase):
    def check_inline_render(self, source, correct_output):
        output = inline.render(source)
        if output != correct_output:
            raise AssertionError('\n'.join((source, output, correct_output)))

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
            '_one_ **two** *three*',
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

    def test_mix_underscore_asterisk(self):
        # We should allow underscores and asterisks to be mixed in any way,
        # including open with one and closing with the other, or even "*_" for
        # strong.  Create a semi-complex case and test all permutations
        source = '***one**two*three'
        correct_output = '<em><strong>one</strong>two</em>three'
        source_parts = source.split('*')
        for delims in itertools.product('*_', repeat=len(source_parts)-1):
            case_parts = []
            for p, d in zip(source_parts, delims):
                case_parts.extend((p, d))
            case_parts.append(source_parts[-1])
            self.check_inline_render(''.join(case_parts), correct_output)

    # link rendering
    def test_auto_link(self):
        self.check_inline_render(
            'http://example.com/',
            '<a href="http://example.com/">http://example.com/</a>')

    def test_auto_link_no_scheme(self):
        self.check_inline_render(
            'example.com',
            '<a href="http://example.com">example.com</a>')

    def test_manual_link(self):
        self.check_inline_render('[Link Text](http://example.com/)',
                                 '<a href="http://example.com/">Link Text</a>')

    def test_escaping(self):
        self.check_inline_render(""" "<>& """, ' &quot;&lt;&gt;&amp; ')

    # everything together
    def test_mixed_markup(self):
        self.check_inline_render(
            'example.com **[Text](http://example.com/link)**',
            '<a href="http://example.com">example.com</a> '
            '<strong><a href="http://example.com/link">Text</a></strong>')

def lines(*text_list):
    """Make a bunch of lines."""
    return '\n'.join(text_list) + '\n'

class BlockMarkdownTestBase(TestCase):
    def check_render_markdown(self, source, correct_output):
        output = render.render_markdown(source)
        if output != correct_output:
            raise AssertionError(
                '\n--- source ---\n{}\n--- output ---\n{}'
                '\n--- correct ---\n{}\n--------------'.format(
                    source, output, correct_output))

class TestText(BlockMarkdownTestBase):
    def check_text_render(self, source, paragraphs):
        self.check_render_markdown(source, lines(
            *tuple('<p>{}</p>'.format(p) for p in paragraphs)))

    def test_text(self):
        self.check_text_render(lines('first',
                                      '',
                                      'second'),
                               ['first', 'second'])

    def test_multiline_text(self):
        self.check_text_render(lines('first',
                                     'second'),
                               ['first second'])

    def test_empty_lines_ignored(self):
        self.check_text_render(lines('first',
                                     '', '', '', '',
                                     'second'),
                               ['first', 'second'])

    def test_inline_render(self):
        self.check_text_render(lines('one *one*',
                                     'two **two**'),
                               ['one <em>one</em> two <strong>two</strong>'])

class TestQuotes(BlockMarkdownTestBase):
    def check_quote_render(self, source, quote_parts):
        correct_parts = ['<blockquote>']
        correct_parts.extend('  <p>{}</p>'.format(q) for q in quote_parts)
        correct_parts.append('</blockquote>')
        self.check_render_markdown(source, lines(*correct_parts))

    def test_quote(self):
        self.check_quote_render(lines('> my',
                                      '>quote'),
                                ['my quote'])

    def test_multi_paragraph_quote(self):
        self.check_quote_render(lines('> my',
                                      '>',
                                      '>quote'),
                                ['my', 'quote'])

    def test_leading_space_ignored(self):
        self.check_quote_render(lines('>',
                                      '> ',
                                      '> quote'),
                                ['quote'])

    def test_trailing_space_ignored(self):
        self.check_quote_render(lines('> quote',
                                      '> ',
                                      '>'),
                                ['quote'])

    def test_extra_middle_space_ignored(self):
        self.check_quote_render(lines('> one',
                                      '> ',
                                      '>',
                                      '> ',
                                      '>two'),
                                ['one', 'two'])

    def test_extra_crocs_ignored(self):
        self.check_quote_render(lines('>>> one',
                                      '>>> ',
                                      '>>>two'),
                                ['one', 'two'])

    def test_inline_render(self):
        self.check_quote_render(lines('> *one*',
                                      '> *two*',
                                      '>',
                                      '> *three*'),
                                ['<em>one</em> <em>two</em>', '<em>three</em>'])

class TestHeadings(BlockMarkdownTestBase):
    def test_heading(self):
        self.check_render_markdown('# heading', '<h2>heading</h2>')

    def test_subheading(self):
        self.check_render_markdown('## heading', '<h3>heading</h3>')

    def test_extra_hashes_ignored(self):
        self.check_render_markdown('### heading', '<h3>heading</h3>')
        self.check_render_markdown('####### heading', '<h3>heading</h3>')

    def test_multiline(self):
        self.check_render_markdown(lines('# one', '# two'),
                                   '<h2>one two</h2>')

    def test_inline_render(self):
        self.check_render_markdown(lines('# *heading*'),
                                   '<h2><em>heading</em></h2>')
        self.check_render_markdown(lines('## *heading*'),
                                   '<h3><em>heading</em></h3>')

class TestList(BlockMarkdownTestBase):
    def check_list(self, source, correct_items, ordered=False):
        if ordered:
            tag_name = 'ol'
        else:
            tag_name = 'ul'
        correct_parts = ['<{}>'.format(tag_name)]
        correct_parts.extend('  <li>{}</li>'.format(i) for i in correct_items)
        correct_parts.append('</{}>'.format(tag_name))
        self.check_render_markdown(source, lines(*correct_parts))

    def test_list(self):
        self.check_list(lines('* one',
                              '*two',
                              '*  three'),
                        ['one', 'two', 'three'])

    def test_dash(self):
        self.check_list(lines('- one',
                              '-two',
                              '-  three'),
                        ['one', 'two', 'three'])

    def test_ordered_list(self):
        self.check_list(lines('1. one',
                              '2.two',
                              '3.  three'),
                        ['one', 'two', 'three'],
                        ordered=True)

    def test_any_number_works(self):
        self.check_list(lines('1. one',
                              '1.two',
                              '1.  three'),
                        ['one', 'two', 'three'],
                        ordered=True)

    def test_list_continuation(self):
        self.check_list(lines('* one',
                              '  two',
                              ' three',
                              '* four'),
                        ['one two three', 'four'])

    def test_nested_list(self):
        self.check_render_markdown(
            lines('* one',
                  '*  two',
                  '  * two a',
                  '  * two',
                  '    b',
                  '  * two',
                  ' c',
                  # c should continue the nested list even though there's
                  # one 1 space
                  '* three'
                 ),
            lines('<ul>',
                  '  <li>one</li>',
                  '  <li>two</li>',
                  '  <li><ul>',
                  '    <li>two a</li>',
                  '    <li>two b</li>',
                  '    <li>two c</li>',
                  '  </ul></li>',
                  '  <li>three</li>',
                  '</ul>'))

    def test_type_switch(self):
        self.check_render_markdown(
            lines('* one',
                  '*  two',
                  '1. three',
                  '2. four',
                 ),
            lines('<ul>',
                  '  <li>one</li>',
                  '  <li>two</li>',
                  '</ul>',
                  '<ol>',
                  '  <li>three</li>',
                  '  <li>four</li>',
                  '</ol>'))

    def test_mixed_nested_list(self):
        self.check_render_markdown(
            lines('* one',
                  '* two',
                  '  1. two a',
                  '  2. two b',
                  '* three'),
            lines('<ul>',
                  '  <li>one</li>',
                  '  <li>two</li>',
                  '  <li><ol>',
                  '    <li>two a</li>',
                  '    <li>two b</li>',
                  '  </ol></li>',
                  '  <li>three</li>',
                  '</ul>'))

    def test_inline_render(self):
        self.check_render_markdown(
            lines('* **one**',
                  '* _two_'),
            lines('<ul>',
                  '  <li><strong>one</strong></li>',
                  '  <li><em>two</em></li>',
                  '</ul>'))
