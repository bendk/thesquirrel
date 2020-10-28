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

import hashlib
import re

from django.template.loader import render_to_string

# set of rules to generate video hosts
class VideoHostRule(object):
    split_url_re = re.compile(r'(https?://)?'
                              r'(?P<domain>[\w\.-]+)'
                              r'(?P<rest>/.*)$')

    def __init__(self, name, domain, regex):
        self.name = name
        self.domain = domain
        self.regex = re.compile(regex)

    def test(self, url):
        match = self.split_url_re.match(url)
        if not match:
            return None
        if not match.group('domain').endswith(self.domain):
            return None
        match2 = self.regex.match(match.group('rest'))
        if match2:
            return match2.groupdict()
        else:
            return None

class HTML5VideoRule(object):
    valid_extensions = set(['ogv', 'ogg', 'mp4', 'm4v', 'webm'])
    name = 'html5'

    def test(self, url):
        if url.rsplit('.', 1)[-1] in self.valid_extensions:
            return {
                'url': url,
                'video_id': hashlib.md5(url).hexdigest()
            }

video_rules = [
    VideoHostRule('youtube', 'youtube.com', r'.*?v=(?P<video_id>[\w-]+)'),
    VideoHostRule('youtube', 'youtu.be', r'/(?P<video_id>[\w-]+)'),
    VideoHostRule('vimeo', 'vimeo.com', r'/(channels/\w+/)?(?P<video_id>\d+)'),
    VideoHostRule('dailymotion', 'dailymotion.com',
                  r'/video/(?P<video_id>[\w-]+)'),
    HTML5VideoRule(),
]

def render_video_for_url(url):
    for rule in video_rules:
        match_info = rule.test(url)
        if match_info is None:
            continue
        template = 'editor/video-{}.html'.format(rule.name)
        return render_to_string(template, match_info)
    return render_to_string('editor/video-unknown.html')
