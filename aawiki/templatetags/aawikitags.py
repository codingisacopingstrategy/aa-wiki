import re
import time
from datetime import datetime
from django.template.defaultfilters import stringfilter
from django import template
from aawiki import utils
from aawiki.mdx import get_markdown
from aawiki import tags
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def fromtimestamp(value):
    return datetime.fromtimestamp(value)


@register.filter
def epock2datetime(value):
    return datetime(*time.gmtime(value)[:6])


@register.filter
@stringfilter
def escape_newlines(value):
    """
    Escapes newlines sequences 
    """
    #return value.encode('unicode-escape')
    return value.replace('\n', r'\n')


@register.filter
@stringfilter
def wikify(value):
    """
    Wikifies the given string
    """
    return utils.wikify(value)


@register.filter
@stringfilter
def render_aatags(value):
    """
    Renders aa tags
    """
    return "".join(tags.render_tpl(value))


class MarkdownConvertor(template.Node):
    def __init__(self, value, var_name, meta_name):
        self.value = template.Variable(value)
        self.var_name = var_name
        self.meta_name = meta_name
    def render(self, context):
        md = get_markdown()
        html = md.convert(self.value.resolve(context))
        # We use context.dicts[0] instead of context in order to access the
        # variables in any template blocks
        # See http://od-eon.com/blogs/liviu/scope-variables-template-blocks/
        context.dicts[0][self.var_name] = mark_safe(html)
        if hasattr(md, "Meta"):
            context.dicts[0][self.meta_name] = md.Meta
        else:
            context.dicts[0][self.meta_name] = {}
        return ''

def do_get_markdown_for(parser, token):
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) as (\w+) (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    format_string, var_name, meta_name = m.groups()
    return MarkdownConvertor(format_string, var_name, meta_name)

register.tag('get_markdown_for', do_get_markdown_for)


@register.filter
@stringfilter
def aamarkdown (value):
    """ 
    markdown with aa extensions
    """
    md = get_markdown()
    return md.convert(value)
aamarkdown.is_safe = True

@register.filter
@stringfilter
def aasimplemarkdown (value):
    """ 
    markdown with aa extensions
    """
    md = get_markdown(simple=True)
    return md.convert(value)
aamarkdown.is_safe = True
