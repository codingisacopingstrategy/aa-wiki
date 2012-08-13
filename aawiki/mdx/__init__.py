#! /usr/bin/env python2


"""
Active Archives Markdown init function
======================================

It gathers the various AA Extensions for Python-Markdown

Requires Python-Markdown 2.0+.
"""


import markdown
try: from markdown.util import etree
except ImportError: from markdown import etree
import mdx_timecodes

from aawiki.utils import url_for_pagename
import urlparse


def aa_make_link(md, rel, target, label):
    a = etree.Element('a')

    # FIXME: This was added to give anchor support within a wiki page.
    #        Many link styles are not taken into account yet.
    parts = urlparse.urlparse(target)

    if parts.fragment and not (parts.scheme or parts.netloc):
        href = "#%s" % parts.fragment
    elif parts.scheme:
        href = target
        a.set('target', '_blank')
    else:
        href = url_for_pagename(target)
    a.set('href', href)

    if rel and rel == "aa:embed":
        img = etree.Element('img')
        img.set('src', '/static/aawiki/img/ajax-loader.gif')
        a.append(img)

    a.set('rel', rel or 'aa:link')

    if label:
        if label.startswith('|'):
            label, filter_ = None, label[1:] 
        else:
            try:
                label, filter_ = label.split('|', 1)
            except ValueError:
                filter_ = None 
        if filter_:
            a.set('data-filter', filter_.strip())

    a.text = label or target
    return a


def aa_make_elt (md, rel, target, label):
     if rel == "dc:title":
         elt = markdown.util.etree.Element('cite')
     else:
         elt = markdown.util.etree.Element('span')
     elt.set('content', target)
     elt.text = label or target
     if rel:
         elt.set('property', rel)
     return elt


def get_markdown(simple=False):
    """
    Returns a Markdown instance with the appropriate extensions for active
    archives wiki.
    """
    extension_configs = {
        'semanticwikilinks': [('make_link', aa_make_link)],
        'semanticdata': [('make_elt', aa_make_elt)],
    }
    extensions = ["attr_list", "cite", "def_list", "del_ins", "semanticdata",
            "semanticwikilinks", mdx_timecodes.makeExtension()]

    if not simple:
        extensions.extend(["footnotes", "headerid", "meta", "outline"])

    return markdown.Markdown(output_format="html5", extensions=extensions, 
                             extension_configs=extension_configs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
