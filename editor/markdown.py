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

import mistune

class Renderer(mistune.Renderer):
    def header(self, text, level, raw=None):
        # force all headings to be h2 or h3
        if level == 1:
            level = 2
        else:
            level = 3
        return super(Renderer, self).header(text, level, raw)

    def block_quote(self, text):
        print text
        return super(Renderer, self).block_quote(text)

renderer = Renderer()
md = mistune.Markdown(renderer=renderer)

def render(source):
    return md.render(source)
