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

"""editor.formatting.inline -- Render inline text """

import re
from cgi import escape

from django.utils.html import urlize

link_re = re.compile(r'\[([^\]]+)]\(([^)]+)\)')
em_strong_delimiter_re = re.compile(
    r'(?<![*_])' # no delimiters before the match
    r'([*_]{1,3})' # 1-3 delimiters make up the match
    r'(?![*_])' # no delimiters after the match
)
def chunked_render(source_parts, join_str=' '):
    """Low-level rendering

    This method is used by the block renderer, which splits up the input
    string into lines.  This method works with lists of strings to complement
    that.

    Note:
        em and strong will be matched between different lines, but URLs won't

    Args:
        source_parts: list of strings to render inline
        join_str: between each string in the list, we will insert this string

    Returns:
        list of strings that should be joined together to make the output

    """
    formatted_source_parts = []
    formatted_source_parts.append(urlize_escape_and_link(source_parts[0]))
    for part in source_parts[1:]:
        formatted_source_parts.append(join_str)
        formatted_source_parts.append(urlize_escape_and_link(part))

    return sub_em_and_strong(formatted_source_parts)

def urlize_escape_and_link(source):
    source = escape(source, quote=True)
    source = link_re.sub(r'<a href="\2">\1</a>', source)
    return urlize(source)

def sub_em_and_strong(source_parts):
    delimiter_positions = []
    parts = []
    for source_part in source_parts:
        split_part = em_strong_delimiter_re.split(source_part)
        old_len = len(parts)
        parts.extend(split_part)
        delimiter_positions.extend(xrange(old_len + 1, len(parts), 2))

    # we will iterate through the delimiters and replace them

    open_em = open_strong = open_both = None
    # "open" means we've seen 1 of the delimiters, but haven't seen the
    # second to close it.
    insert_before = {}
    # triple delimiters get replaced with 2 tags, insert_before is used
    # to handle the extra tag
    for pos in delimiter_positions:
        count = len(parts[pos])
        if count == 1:
            # single delimiter handles <em>
            if open_em is not None:
                parts[open_em] = '<em>'
                parts[pos] = '</em>'
                open_em = None
            elif open_both is not None:
                # close the <em> and leave an outer '**' delimiter
                insert_before[open_both + 1] = '<em>'
                parts[open_both] = '**'
                parts[pos] = '</em>'
                open_strong = open_both
                open_both = None
            else:
                open_em = pos
        elif count == 2:
            # double delimiter handles <strong>
            if open_strong is not None:
                parts[open_strong] = '<strong>'
                parts[pos] = '</strong>'
                open_strong = None
            elif open_both is not None:
                # close the <strong> and leave an outer '*' delimeter
                insert_before[open_both + 1] = '<strong>'
                parts[pos] = '</strong>'
                parts[open_both] = '*'
                open_em = open_both
                open_both = None
            else:
                open_strong = pos
        elif count == 3:
            # triple delimiter.. this gets a bit complex
            if open_both is not None:
                parts[open_both] = '<strong><em>'
                parts[pos] = '</em></strong>'
                open_both = None
            elif open_strong is not None and open_em is not None:
                parts[open_em] = '<em>'
                parts[open_strong] = '<strong>'
                # need to order the closing tags based on which tag was
                # started first
                if open_em < open_strong:
                    parts[pos] = '</strong></em>'
                else:
                    parts[pos] = '</em></strong>'
                open_both = open_em = None
            elif open_strong:
                # close the strong and leave the remaining delim
                parts[open_strong] = '<strong>'
                insert_before[pos] = '</strong>'
                parts[pos] = '*'
                open_strong = None
                open_em = pos
            elif open_em:
                # close the em and leave the remaining delims
                parts[open_em] = '<em>'
                insert_before[pos] = '</em>'
                parts[pos] = '**'
                open_em = None
                open_strong = pos
            else:
                open_both = pos
    # join everything together and we're done
    combined = []
    for i, part in enumerate(parts):
        if i in insert_before:
            combined.append(insert_before[i])
        combined.append(part)
    return combined

def render(source):
    return ''.join(chunked_render([source]))
