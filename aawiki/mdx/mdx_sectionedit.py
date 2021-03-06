#! /usr/bin/env python2


"""
Splits a markdown source into a flat list of sections.

Markdown extension adds {@data-section=%d} attribute markup to headers.

Provides: sectionalize

    >>> txt = '''
    ... # Section 1
    ... 1984-10-21 00:10,125 -->
    ... Some text
    ... 1984-10-21 00:10,125 --> 01:00:05.300
    ... More text
    ... ## Section 2
    ... 00:10,125 --> Some title {: id="myid" }
    ... Sections can have some more text
    ... 00:30-->00:40
    ... spaces are optionals
    ... ### Section 3
    ... '''

    >>> for match in re.finditer(DATE_RE, txt, re.M):
    ...     print(match.group())
    1984-10-21
    1984-10-21

    >>> for match in re.finditer(TIME_RE, txt, re.M):
    ...     print(match.group())
    00:10,125
    00:10,125
    01:00:05.300
    00:10,125
    00:30
    00:40

    >>> for match in re.finditer(DATETIME_RE, txt, re.M):
    ...     print(match.group())
    1984-10-21 00:10,125
    1984-10-21 00:10,125
    01:00:05.300
    00:10,125
    00:30
    00:40

    >>> for match in re.finditer(DATETIMECODE_RE, txt, re.M):
    ...     print(match.group())
    1984-10-21 00:10,125 -->
    1984-10-21 00:10,125 --> 01:00:05.300
    00:10,125 -->
    00:30-->00:40


    >>> for match in re.finditer(DATETIMECODE_HEADER_RE, txt, re.M):
    ...     print(match.group())
    1984-10-21 00:10,125 -->
    1984-10-21 00:10,125 --> 01:00:05.300
    00:10,125 --> Some title {: id="myid" }
    00:30-->00:40


    >>> for match in re.finditer(HASH_HEADER_RE % '1,6', txt, re.M):
    ...     print(match.group())
    # Section 1
    ## Section 2
    ### Section 3


    >>> for match in re.finditer(HASH_OR_DATETIMECODE_HEADER_RE % '1,6', txt, re.M):
    ...     print(match.group())
    # Section 1
    1984-10-21 00:10,125 -->
    1984-10-21 00:10,125 --> 01:00:05.300
    ## Section 2
    00:10,125 --> Some title {: id="myid" }
    00:30-->00:40
    ### Section 3
"""


import markdown
import re


HASH_HEADER_RE = r'^(?P<level>#{%s})[^#](?P<header>.*?)#*$'
DATE_RE = r'\d\d\d\d-\d\d-\d\d'
TIME_RE = r'(\d\d:)?(\d\d):(\d\d)([,.]\d{1,3})?'
DATETIME_RE = r'(%(DATE_RE)s[ \t]*)?%(TIME_RE)s' % locals()
DATETIMECODE_RE = r'%(DATETIME_RE)s[ \t]*-->([ \t]*%(DATETIME_RE)s)?' % locals()
OTHER_RE = r'.+'
DATETIMECODE_HEADER_RE = r'^%(DATETIMECODE_RE)s(%(OTHER_RE)s)?$' % locals()
HASH_OR_DATETIMECODE_HEADER_RE = "(%s|%s)" % (HASH_HEADER_RE, DATETIMECODE_HEADER_RE)


def spliterator (pattern, text):
    """
    Splits the given text according to the given pattern.

    Yields a dict() where:
    - header is the matched pattern;
    - body is the text until the next match;
    - start is the start character index of the matched section and
    - end is the last character index of the section

        >>> from pprint import pprint
        >>> txt = '''
        ... # Section 1
        ... 1984-10-21 00:10,125 -->
        ... Some text
        ... 1984-10-21 00:10,125 --> 01:00:05.300
        ... More text
        ... ## Section 2
        ... 00:10,125 --> Some title {: id="myid" }
        ... Sections can have some more text
        ... 00:30-->00:40
        ... spaces are optionals
        ... ### Section 3
        ... '''
    
    Splits according to level 1 headers

        >>> pattern = re.compile(HASH_HEADER_RE % '1', re.M)
        >>> for section in spliterator(pattern, txt):
        ...     pprint(section)
        {'body': '\\n1984-10-21 00:10,125 -->\\nSome text\\n1984-10-21 00:10,125 --> 01:00:05.300\\nMore text\\n## Section 2\\n00:10,125 --> Some title {: id="myid" }\\nSections can have some more text\\n00:30-->00:40\\nspaces are optionals\\n### Section 3\\n',
         'end': 231,
         'header': '# Section 1',
         'level': 1,
         'start': 1}


    Splits according to level 2 headers (h2 and timed sections)

        >>> pattern = re.compile(HASH_OR_DATETIMECODE_HEADER_RE % '2', re.M)
        >>> for section in spliterator(pattern, txt):
        ...     pprint(section)
        {'body': '\\nSome text\\n',
         'end': 48,
         'header': '1984-10-21 00:10,125 -->',
         'level': 2,
         'start': 13}
        {'body': '\\nMore text\\n',
         'end': 96,
         'header': '1984-10-21 00:10,125 --> 01:00:05.300',
         'level': 2,
         'start': 48}
        {'body': '\\n', 'end': 109, 'header': '## Section 2', 'level': 2, 'start': 96}
        {'body': '\\nSections can have some more text\\n',
         'end': 182,
         'header': '00:10,125 --> Some title {: id="myid" }',
         'level': 2,
         'start': 109}
        {'body': '\\nspaces are optionals\\n### Section 3\\n',
         'end': 231,
         'header': '00:30-->00:40',
         'level': 2,
         'start': 182}
    """
    matches = pattern.finditer(text)
    match = matches.next()
    start = match.start()
    header = text[match.start():match.end()]
    index = match.end() 

    # Computes the heading level from the regex match group "level". If not
    # present, it means that we are facing a (date)timecode header, hence a
    # level 2 header according to our hierarchy.
    level = len(match.groupdict().get('level') or "##")

    for match in matches:
        if level >= len(match.groupdict().get('level') or "##"):
            yield dict(header=header, body=text[index:match.start()], start=start, end=match.start(), level=level)
            start = match.start()
            header = text[match.start():match.end()]
            index = match.end() 
            level = len(match.groupdict().get('level') or "##")

    yield dict(header=header, body=text[index:], start=start, end=len(text), level=level)


def sectionalize(text, sections=None, offset=0):
    """
        >>> from pprint import pprint
        >>> txt = '''
        ... Some text before
        ... # Section 1
        ... some text
        ... ### Section 3
        ... Some more text
        ... ## Section 2
        ... more text
        ... 00:00:10 --> Timed section
        ... more text
        ... ### Section 3 again
        ... more text
        ... # Section 1 again
        ... more text
        ... '''

        >>> for section in sectionalize(txt):
        ...     print(r'================================')
        ...     print(section['start'], section['end'])
        ...     print(section['header'] + section['body'])
        ================================
        (0, 187)
        <BLANKLINE>
        Some text before
        # Section 1
        some text
        ### Section 3
        Some more text
        ## Section 2
        more text
        00:00:10 --> Timed section
        more text
        ### Section 3 again
        more text
        # Section 1 again
        more text
        <BLANKLINE>
        ================================
        (18, 159)
        # Section 1
        some text
        ### Section 3
        Some more text
        ## Section 2
        more text
        00:00:10 --> Timed section
        more text
        ### Section 3 again
        more text
        <BLANKLINE>
        ================================
        (40, 69)
        ### Section 3
        Some more text
        <BLANKLINE>
        ================================
        (69, 92)
        ## Section 2
        more text
        <BLANKLINE>
        ================================
        (92, 159)
        00:00:10 --> Timed section
        more text
        ### Section 3 again
        more text
        <BLANKLINE>
        ================================
        (129, 159)
        ### Section 3 again
        more text
        <BLANKLINE>
        ================================
        (159, 187)
        # Section 1 again
        more text
        <BLANKLINE>

    We make sure that the section start and end indices are right:

        >>> for section in sectionalize(txt):
        ...     txt1 = section['header'] + section['body']
        ...     txt2 = txt[section['start']:section['end']]
        ...     assert txt1 == txt2
    """
    if sections is None:
        sections = [dict(header='', body=text, start=0, end=len(text), index=0)]

    pattern = re.compile(HASH_OR_DATETIMECODE_HEADER_RE % '1,6', re.M)

    for section in spliterator(pattern, text):
        section['index'] = len(sections)  # numbers the section
        section['start'] = section['start'] + offset  # fixes the offset
        section['end'] = section['end'] + offset
        sections.append(section)

        if section['level'] < 6 and section['body']:
            sectionalize(section['body'], sections, offset=(section['start'] + len(section['header'])))

    return sections


def sectionalize_replace (original_text, section_number, new_text):
    sections = sectionalize(original_text)
    pre_text = original_text[:sections[section_number]['start']]
    post_text = original_text[sections[section_number]['end']:]
    return u"".join([pre_text, new_text, post_text])


class SectionEditExtension(markdown.Extension):
    def __init__(self, configs={}):
        self.config = {}
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        """ Add SectionEditPreprocessor to the Markdown instance. """

        ext = SectionEditPreprocessor(md)
        ext.config = self.config
        md.preprocessors.add('section_edit_block', ext, ">timecodes_block")


class SectionEditPreprocessor(markdown.preprocessors.Preprocessor):
    def run(self, lines):
        """ Adds section numbers to sections """
        newlines = []
        pattern = re.compile(HASH_OR_DATETIMECODE_HEADER_RE % '1,6', re.M)
        i = 0

        for line in lines:
            if pattern.match(line):
                i += 1
                newlines.append(line.rstrip() + " {@data-section=%d}" % i)
            else:
                newlines.append(line)

        return newlines


def makeExtension(configs={}):
    return SectionEditExtension(configs=configs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
