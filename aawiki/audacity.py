# This file is part of Active Archives.
# Copyright 2006-2011 the Active Archives contributors (see AUTHORS)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Also add information on how to contact you by electronic and paper mail.


import re
from aawiki.mdx.mdx_sectionedit import (DATETIMECODE_HEADER_RE, spliterator)
from aawiki.timecode import (timecode_fromsecs, timecode_tosecs)


def audacity_to_srt(data, explicit=False):
    """
    >>> data = '''90,610022  90,610022   first section
    ... 345,271874  345,271874 second section'''
    >>> print(audacity_to_srt(data).strip())
    00:01:30.610 --> 
    <BLANKLINE>
    first section
    <BLANKLINE>
    00:05:45.272 --> 
    <BLANKLINE>
    second section

    >>> data = '''90,610022  345,271874   first section
    ... 345,271874  512,573912 second section'''
    >>> print(audacity_to_srt(data).strip())
    00:01:30.610 --> 
    <BLANKLINE>
    first section
    <BLANKLINE>
    00:05:45.272 --> 00:08:32.574
    <BLANKLINE>
    second section

    >>> data = '''90,610022  345,271874   first section
    ... 345,271874  512,573912 second section'''
    >>> print(audacity_to_srt(data, explicit=True).strip())
    00:01:30.610 --> 00:05:45.272
    <BLANKLINE>
    first section
    <BLANKLINE>
    00:05:45.272 --> 00:08:32.574
    <BLANKLINE>
    second section

    >>> data = '''90,610022  345,271874   first section
    ... 345,271874  512,573912'''
    >>> print(audacity_to_srt(data).strip())
    00:01:30.610 --> 00:05:45.272
    <BLANKLINE>
    first section
    <BLANKLINE>
    00:05:45.272 --> 00:08:32.574
    <BLANKLINE>
    second section
    """
    stack = []

    for line in data.splitlines():
        try:
            (start, end, body) = tuple(line.split(None, 2))
        except ValueError:
            try:
                # A marker without label
                (start, end) = tuple(line.split(None, 1))
                body = ""
            except ValueError:
                # A blank line? Get lost!
                break

        start = float(start.replace(',', '.'))
        end = float(end.replace(',', '.'))

        start = timecode_fromsecs(start, alwaysfract=True, 
                                  alwayshours=True, fractdelim=',')
        end = timecode_fromsecs(end, alwaysfract=True, 
                                alwayshours=True, fractdelim=',')

        # If the end time equals the start time we ommit it.
        if end == start:
            end = ""

        if not explicit:
            # Deletes previous end time if equal to actual start time
            if len(stack) and stack[-1]['end'] == start:
                stack[-1]['end'] = ""

        body = body.replace(r'\n', '\n')

        stack.append({'start': start, 'end': end, 'body': body})

    template = "{e[start]} --> {e[end]}\n\n{e[body]}\n\n"
    return "".join([template.format(e=e) for e in stack])


def srt_to_audacity(data, force_endtime=False):
    """docstring for srt_to_audacity"""
    # FIXME: UnicodeDecodeError...
    # TODO: Regex should not be defined more once within active archives
    TIME_RE = r'(\d\d:)?(\d\d):(\d\d)([,.]\d{1,3})?'
    TIMECODE_RE = r'(?P<start>%(TIME_RE)s)[ \t]*-->([ \t]*(?P<end>%(TIME_RE)s))?' % locals()
    OTHER_RE = r'.+'
    TIMECODE_HEADER_RE = r'^%(TIMECODE_RE)s(%(OTHER_RE)s)?$' % locals()

    pattern = re.compile(TIMECODE_HEADER_RE, re.I | re.M | re.X)

    stack = []
    for t in spliterator(pattern, data):
        m = pattern.match(t['header']).groupdict()

        if force_endtime:
            if len(stack) and stack[-1]['end'] == '':
                stack[-1]['end'] = timecode_tosecs(m['start'])
            end = timecode_tosecs(m['end']) or ''
        else:
            end = timecode_tosecs(m['end']) or timecode_tosecs(m['start'])

        stack.append({
            'start': timecode_tosecs(m['start']),
            'end': end,
            'body': t['body'].strip('\n').replace('\n', r'\n'),
        })

    template = u"{e[start]}\t{e[end]}\t{e[body]}\n"
    return u"".join([template.format(e=e) for e in stack])


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    f = open('/tmp/bla.srt', 'r')
    data = f.read()
    f.close()
    #print(audacity_to_srt(data))
    print(srt_to_audacity(data))
