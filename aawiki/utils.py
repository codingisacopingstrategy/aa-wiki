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


"""
Utilities specific to the core application
"""

import urllib
import re
import string
from django.core.urlresolvers import reverse


def url_for_pagename(name):
    """ Convenience function to map a name to a page (partial) URL """
    return reverse('aawiki:page-detail', args=[wikify(name)])

def pagename_for_url(url):
    """ Convenience function to map a name to a page (partial) URL """
    url = url.rstrip("/")
    name = dewikify(url[url.rindex("/")+1:])
    return name

def wikify(name):
    """
    Turns a "raw" name into a URL wiki name (aka slug)

    1. Spaces turn into underscores.
    2. The First letter is forced to be Uppercase (normalization).
    3. For the rest, non-ascii chars get percentage escaped.

    (Unicode chars be (properly) encoded to bytes and urllib.quote'd to double escapes like "%23%25" as required)

    >>> wikify("my page name")
    'My_page_name'

    >>> wikify(";/?:@=#&")
    '%3B%2F%3F%3A%40%3D%23%26'
    """
    name = name.strip().replace(" ", "_")

    if len(name):
        name = name[0].upper() + name[1:]

    if (type(name) == unicode):
        # urllib.quoting(unicode) with accents freaks out so encode to bytes
        name = name.encode("utf-8")

    return urllib.quote(name, safe="")


def dewikify(name):
    """
    Turns URL name/slug into a proper name (reverse of wikify).
    Requires: name may be unicode, str
    Returns: str

    NB dewikify(wikify(name)) may produce a different name (first letter gets capitalized)
    """
    if (type(name) == unicode):
        # urllib.unquoting unicode with accents freaks! so encode to bytes
        name = name.encode("utf-8")
    name = urllib.unquote(name)
    name = name.replace("_", " ")
    return name

def convert_line_endings(temp, mode):
        #modes:  0 - Unix, 1 - Mac, 2 - DOS
        if mode == 0:
            temp = string.replace(temp, '\r\n', '\n')
            temp = string.replace(temp, '\r', '\n')
        elif mode == 1:
            temp = string.replace(temp, '\r\n', '\r')
            temp = string.replace(temp, '\n', '\r')
        elif mode == 2:
            temp = re.sub("\r(?!\n)|(?<!\r)\n", "\r\n", temp)
        return temp
