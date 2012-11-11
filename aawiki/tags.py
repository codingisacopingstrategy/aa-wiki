"""
Code is derived from
http://effbot.org/zone/django-simple-template.htm
"""


import re
from rdfutils import query
from urlparse import urlparse
from aacore import RDF_MODEL


def render_tpl(template):
    """
    >>> txt = "this is a {% template tag %}"
    >>> print(render_tpl(txt))
    >>> txt = "this is a {% template tag not closed"
    >>> print(render_tpl(txt))
    >>> txt = "this is all our pages: {% list_pages %}"
    >>> print(render_tpl(txt))
    >>> txt = "this is all our pages: {% list_pages ldskjdslkdsj"
    >>> print(render_tpl(txt))
    >>> txt = "this is all our pages: {% list_pages "
    >>> print(render_tpl(txt))
    """
    next = iter(re.split("({%|%})", template)).next
    data = []
    try:
        token = next()
        while 1:
            if token == "{%": # variable
                data.append(render_tag(next()))
                if next() != "%}":
                    pass
            else:
                data.append(token) # literal
            token = next()
    except StopIteration:
        pass
    return data


def render_tag(tag):
    tag = tag.strip()
    try:
        (tag, arguments) = tag.split(" ", 1)
    except ValueError:
        arguments = None

    tags = {}
    for t in AATag.__subclasses__():
        tags[t.name] = t

    try:
        return tags[tag](arguments).output
    except KeyError:
        return "<mark>The %s tag doesn't exists</mark>" % tag


class AATag(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.output = self.run()


class AASparql(AATag):
    name = "sparql"

    def run(self):
        return "ok"


class AAPageList(AATag):
    name = "pagelist"

    def run(self):

        ret = query("""\
                SELECT DISTINCT ?url ?title 
                WHERE { 
                    ?url <http://www.w3.org/1999/xhtml/vocab#index> ?c. 
                    ?url <http://purl.org/dc/elements/1.1/title> ?title. 
                }""", RDF_MODEL)

        foo = ["<ul>"]
        for i in ret:
            path = urlparse(str(i['url'])).path
            foo.append('<li><a href="%s">%s</a></li>' % (path, str(i['title'])))
        foo.append("</ul>")
        return "".join(foo)


class AAAnnotations(AATag):
    name = "annotations"

    def run(self):
        ret = query("""
                SELECT ?a WHERE { 
                    <http://www.lemonde.fr/> <http://activearchives.org/terms/annotation> ?a . 
                }""", RDF_MODEL)
        foo = []
        for i in ret:
            foo.append("<section class='section2'>%s</section>" % str(i['a']))
        return "".join(foo)


class AAAuthors(AATag):
    name = "authors"

    def run(self):
        print self.args
        ret = query("""
                SELECT DISTINCT ?object ?subject WHERE { 
                    ?object <http://activearchives.org/terms/author> ?subject . 
                    FILTER (REGEX(?subject, "^%s"))
                }""" % self.args[0], RDF_MODEL)
        foo = ["<ul>"]
        for i in ret:
            foo.append("<li><a href='%s'>%s</a></li>" % (str(i['object']), str(i['subject'])))
        foo.append("</ul>")
        return "".join(foo)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
