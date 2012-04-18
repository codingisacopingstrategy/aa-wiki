"""
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


#HASH_HEADER_RE = r'^(?P<level>#{%s})(?P<header>.*?)#*$'
HASH_HEADER_RE = r'^(?P<level>#{%s})[^#](?P<header>.*?)#*$'
DATE_RE = r'\d\d\d\d-\d\d-\d\d'
TIME_RE = r'(\d\d:)?(\d\d):(\d\d)([,.]\d{1,3})?'
DATETIME_RE = r'(%(DATE_RE)s[ \t]*)?%(TIME_RE)s' % locals()
DATETIMECODE_RE = r'%(DATETIME_RE)s[ \t]*-->([ \t]*%(DATETIME_RE)s)?' % locals()
OTHER_RE = r'.+'
DATETIMECODE_HEADER_RE = r'^%(DATETIMECODE_RE)s(%(OTHER_RE)s)?$' % locals()
HASH_OR_DATETIMECODE_HEADER_RE = "(%s|%s)" % (HASH_HEADER_RE, DATETIMECODE_HEADER_RE)


def spliterator (pattern, text, returnLeading=False):
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
         'start': 1}


    Splits according to level 2 headers (h2 and timed sections)

        >>> pattern = re.compile(HASH_OR_DATETIMECODE_HEADER_RE % '2', re.M)
        >>> for section in spliterator(pattern, txt):
        ...     pprint(section)
        {'body': '\\nSome text\\n',
         'end': 48,
         'header': '1984-10-21 00:10,125 -->',
         'start': 13}
        {'body': '\\nMore text\\n',
         'end': 96,
         'header': '1984-10-21 00:10,125 --> 01:00:05.300',
         'start': 48}
        {'body': '\\n', 'end': 109, 'header': '## Section 2', 'start': 96}
        {'body': '\\nSections can have some more text\\n',
         'end': 182,
         'header': '00:10,125 --> Some title {: id="myid" }',
         'start': 109}
        {'body': '\\nspaces are optionals\\n### Section 3\\n',
         'end': 231,
         'header': '00:30-->00:40',
         'start': 182}

    """
    matches = pattern.finditer(text)
    match = matches.next()
    start = match.start()
    header = text[match.start():match.end()]
    index = match.end() 

    for match in matches:
        yield dict(header=header, body=text[index:match.start()], start=start, end=match.start())
        start = match.start()
        header = text[match.start():match.end()]
        index = match.end() 

    yield dict(header=header, body=text[index:], start=start, end=len(text))


def sectionalize(text, depth=1, sections=None, offset=0):
    """
        >>> from pprint import pprint
        >>> txt = '''
        ... # Section 1
        ... some text
        ... 1984-10-21 00:10,125 -->
        ... Some more text
        ... # Section 1 again
        ... more text
        ... '''

        >>> for section in sectionalize(txt):
        ...     pprint(section)
        {'body': '\\nsome text\\n1984-10-21 00:10,125 -->\\nSome more text\\n',
         'end': 63,
         'header': '# Section 1',
         'index': 0,
         'start': 1}
        {'body': '\\nSome more text\\n',
         'end': 63,
         'header': '1984-10-21 00:10,125 -->',
         'index': 1,
         'start': 23}
        {'body': '\\nmore text\\n',
         'end': 91,
         'header': '# Section 1 again',
         'index': 2,
         'start': 63}

    We make sure that the section start and end indices are right:

        >>> for section in sectionalize(txt):
        ...     txt1 = section['header'] + section['body']
        ...     txt2 = txt[section['start']:section['end']]
        ...     assert txt1 == txt2
    """
    if sections is None:
        sections = []
        #sections = [dict(header='', body=text, start=0, end=len(text), index=0)]

    if depth == 2:
        pattern = re.compile(HASH_OR_DATETIMECODE_HEADER_RE % depth, re.M)
    else:    
        pattern = re.compile(HASH_HEADER_RE % depth, re.M)

    for section in spliterator(pattern, text):
        section['index'] = len(sections)  # numbers the section
        section['start'] = section['start'] + offset  # fixes the offset
        section['end'] = section['end'] + offset
        sections.append(section)

        if depth < 6 and section['body']:
            sectionalize(section['body'], depth + 1, sections, offset=(section['start'] + len(section['header'])))

    return sections


def sectionalize_2(text, depth=1, sections=None, offset=0):
    """
        >>> from pprint import pprint
        >>> txt = '''
        ... # Section 1
        ... some text
        ... ### Section 3
        ... Some more text
        ... ## Section 1 again
        ... more text
        ... '''

        >>> for section in sectionalize_2(txt):
        ...     print(section['start'], section['end'])
        ...     print(section['header'] + section['body'])
        ...     print('***********************************')

    We make sure that the section start and end indices are right:

        >>> for section in sectionalize_2(txt):
        ...     txt1 = section['header'] + section['body']
        ...     txt2 = txt[section['start']:section['end']]
        ...     assert txt1 == txt2
    """
    if sections is None:
        sections = []
        #sections = [dict(header='', body=text, start=0, end=len(text), index=0)]

    repetitions = '%s,6' % depth
    pattern = re.compile(HASH_HEADER_RE % repetitions, re.M)

    for section in spliterator(pattern, text):
        section['index'] = len(sections)  # numbers the section
        section['start'] = section['start'] + offset  # fixes the offset
        section['end'] = section['end'] + offset
        sections.append(section)

        if depth < 6 and section['body']:
            sectionalize_2(section['body'], depth + 1, sections, offset=(section['start'] + len(section['header'])))

    return sections


if __name__ == "__main__":
    import doctest
    doctest.testmod()
