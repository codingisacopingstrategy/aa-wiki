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
import urllib

try: import simplejson as json
except ImportError: import json

from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext 
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from aacore.models import Namespace

from aawiki.filters import *
from aawiki.utils import dewikify
from aawiki.mdx.mdx_sectionedit import sectionalize, spliterator
from aawiki.forms import PageEditForm, AnnotationImportForm
from aawiki.audacity import audacity_to_srt
from aawiki.timecode import timecode_tosecs

from aawiki.settings import REPO_PATH
from pygit2 import GIT_SORT_TIME, Repository, Signature, init_repository
import time
from diff_match_patch import diff_match_patch
from aacore.sniffers import AAResource

from aawiki.api import PageResource
from tastypie.exceptions import NotFound


try:
    repo = Repository(REPO_PATH)
except KeyError:
    repo = init_repository(REPO_PATH, True)
    # create a tree with blob out of memory
    #blob_oid = repo.create_blob("This is the README file.")
    builder = repo.TreeBuilder()
    #builder.insert('README', blob_oid, 0100644)
    tree_oid = builder.write()

    author = committer = Signature('foo bar', 'foo@bar.de', int(time.time()), 0)

    # commit everything (as initial commit)
    repo.create_commit(
      'HEAD',
      author,
      committer,
      'initial commit',
      tree_oid,
      []
    )


def embed (request):
    """
    Receives a request with parameters URL and filter.
    Returns a JSON containing content of the embed.
    """
    url = request.REQUEST.get("url")
    # ALLOW (authorized users) to trigger a resource to be added...
    if url.startswith("http://"):
        # TODO: REQUIRE LOGIN TO ACTUALLY ADD...
        AAResource(url).index()

    ### APPLY FILTERS (if any)
    pipeline = request.REQUEST.get("filter", "embed").strip()
    filters = {}

    for filter_ in AAFilter.__subclasses__():
        filters[filter_.name] = filter_

    stdin = {
        'original_url': url,
        #'local_url': Resource.objects.get(url=url).get_local_url(),
        #'local_path': Resource.objects.get(url=url).get_local_file(),
        'local_url': "",
        'local_path': "",
        'output': 'None',
        'extra_css': [],
        'extra_js': [],
        'script': "",
    }

    for command in [x.strip() for x in pipeline.split("|")]:
        if ":" in command:
            (filter_, arguments) = command.split(":", 1)
            filter_.strip()
            command.strip()
        else:
            (filter_, arguments) = (command.strip(), None)
        try:
            stdin = filters[filter_](arguments, stdin).stdout
        except KeyError:
            stdin['output'] = """The "%s" filter doesn't exist""" % filter_
            break
    
    browseurl = reverse("aa-browse") + "?" + urllib.urlencode({'uri': url})
    ret = """
<div class="aa_embed">
    <div class="links">
        <a class="directlink" href="%(url)s">URL</a>
        <a class="browselink" target="browser" href="%(browseurl)s">metadata</a>
    </div>
    <div class="body">%(embed)s</div>
</div>""".strip()

    content = ret % {'url': url, 'browseurl': browseurl, 'embed': stdin['output']}
    return HttpResponse(json.dumps({"ok": True, "content": content, 'extra_css': stdin['extra_css'], 
                        'extra_js': stdin['extra_js'], 'script': stdin['script']}), 
                        mimetype="application/json");


@login_required
def annotation_import(request, slug, section):
    """
    Saves the file directly from the request object.
    Disclaimer:  This is code is just an example, and should
    not be used on a real website.  It does not validate
    file uploaded:  it could be used to execute an
    arbitrary script on the server.
    """
    context = {}
    name = dewikify(slug)
    page = Page.objects.get(name=name)

    if request.method == 'POST':
        form = AnnotationImportForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            data = ""
            for chunk in f.chunks():
                data += chunk

            srt = unicode(audacity_to_srt(data).decode('utf-8'))

            # Preserves the old header, because audacity only keeps timed section.
            # TODO: decide wether it should be handled here or in sectionalize_replace
            section = int(section)
            header = sectionalize(page.content)[section]['header'] + "\n\n"

            context = {'content': header + srt, 'section': section, 'page': page}
            return render_to_response("aawiki/annotation_import_confirm.html", context, 
                                      context_instance=RequestContext(request))
    else:
        form = AnnotationImportForm()
        context['form'] = form
        return render_to_response("aawiki/annotation_import.html", context, 
                                  context_instance=RequestContext(request))


def annotation_export(request, slug, section, _format="audacity",
                      force_endtime=False):
    context = {}
    name = dewikify(slug)
    page = Page.objects.get(name=name)

    section = sectionalize(page.content)[int(section)]

    # TODO: Regex should not be defined more once within active archives
    TIME_RE = r'(\d\d:)?(\d\d):(\d\d)([,.]\d{1,3})?'
    TIMECODE_RE = r'(?P<start>%(TIME_RE)s)[ \t]*-->([ \t]*(?P<end>%(TIME_RE)s))?' % locals()
    OTHER_RE = r'.+'
    TIMECODE_HEADER_RE = r'^%(TIMECODE_RE)s(%(OTHER_RE)s)?$' % locals()

    pattern = re.compile(TIMECODE_HEADER_RE, re.I | re.M | re.X)

    stack = []
    for t in spliterator(pattern, section['header'] + section['body']):
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
            'body': t['body'].strip('\n'),
        })

    context = {'sections': stack}

    return render_to_response("aawiki/annotation_export.audacity", context, 
                              context_instance=RequestContext(request), 
                              mimetype="text/plain;charset=utf-8")


@login_required
def file_upload(request):
    for f in request.FILES.getlist('file'):
        destination = open(os.path.join(settings.AA_UPLOAD_DIR, f.name), 'wb+')
        destination.write(f.file.read())
        destination.close()
    return HttpResponse("Seems like it worked!")


def page_detail(request, slug):
    try:
        page = PageResource().obj_get(request, name=slug)
    except NotFound:
        # Redirects to the edit page
        url = reverse('aawiki:page-edit', kwargs={'slug': slug})
        return redirect(url)

    ctx= {'namespaces': Namespace.objects.all(), 'slug': slug, 'content': page.content}
    response = render_to_response("aawiki/page_detail.html", ctx, context_instance=RequestContext(request))

    # Forces the page to reload
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Expires'] = '-1'
    response['Pragma'] = 'no-cache'

    return response


@login_required
def page_edit(request, slug):
    ctx = {"slug": slug}

    if request.method == "POST": # A form was sent: processes it
        form = PageEditForm(request.POST)

        if form.is_valid():
            page = PageResource()
            bundle = page.build_bundle(request=request, data=form.data.dict())

            try:
                page.obj_update(bundle, request=request, name=slug)
            except NotFound:
                bundle.data['name'] = slug
                page.obj_create(bundle, request=request)

            # indexes the page in the RDF store
            url = reverse('aawiki:page-detail', kwargs={'slug': slug})
            AAResource("http://localhost:8000" + url).index()

            return redirect(url)

    else:
        try:
            page = PageResource().obj_get(request, name=slug)
            content = page.content
        except NotFound:
            content = ""

        ctx['form'] = PageEditForm(initial={"content": content})

    return render_to_response("aawiki/page_edit.html", ctx, context_instance=RequestContext(request))


@login_required
def page_flag(request, slug):
    """
    Flags the last commit the edit of a :model:`aawiki.Page` as a major one

    Returns "OK"
    """
    name = dewikify(slug)
    page = Page.objects.get(name=name)
    message = request.REQUEST.get('message', None)
    page.commit(amend=True, message=message)
    return HttpResponse("Seems like it worked!")


def page_history(request, slug): 
    """
    Displays the commit list of the Git repository associated to a page.
    """
    def iter_commits(name):
        last_commit = None
        last_oid = None

        # loops through all the commits
        for commit in repo.walk(repo.head.oid, GIT_SORT_TIME):
            # checks if the file exists
            if name in commit.tree:
                # has it changed since last commit?
                # let's compare it's sha with the previous found sha
                oid = commit.tree[name].oid
                has_changed = (oid != last_oid and last_oid)

                if has_changed:
                    yield last_commit

                last_oid = oid
            else:
                last_oid = None

            last_commit = commit

        if last_oid:
            yield last_commit


    context = {} 
    context['commits'] = iter_commits(slug)
    context['slug'] = slug
    context['content'] = "bla"

    return render_to_response("aawiki/page_history.html", context,
            context_instance=RequestContext(request))


def page_diff(request, slug): 
    """
    Displays a comparision of two revisions of a page.
    """
    def diff_prettyXhtml(self, diffs):
        """
        Extends google's diff_patch_match
        Similar to diff_prettyHtml but returns an XHTML valid code
        """
        html = []
        i = 0
        for (op, data) in diffs:
            text = (data.replace("&", "&amp;").replace("<", "&lt;")
                     .replace(">", "&gt;").replace("\n", "<br />"))
            if op == self.DIFF_INSERT:
                html.append('<ins class="added" title="i=%i">%s</ins>' % (i, text))
            elif op == self.DIFF_DELETE:
                html.append('<del class="deleted" title="i=%i">%s</del>' % (i, text))
            elif op == self.DIFF_EQUAL:
                html.append('<span class="equal" title="i=%i">%s</span>' % (i, text))
            if op != self.DIFF_DELETE:
                i += len(data)
        return "".join(html)

    context = {} 
    context["slug"] = slug

    c1 = request.GET.get("c1", None)
    c2 = request.GET.get("c2", None)

    f1 = repo[c1].tree[slug].to_object().data
    f2 = repo[c2].tree[slug].to_object().data
    ui = diff_match_patch()
    diff = ui.diff_main(f1, f2)
    ui.diff_cleanupSemantic(diff)
    context['content'] = diff_prettyXhtml(ui, diff)
    context['c1'] = repo[c1]
    context['c2'] = repo[c2]

    return render_to_response("aawiki/page_diff.html", context,
            context_instance=RequestContext(request))


def sandbox(request):
    """
    Sample page to test wikitext / embed processing. Unlike a real wiki
    sandbox, this page is always ephemeral (nothing is saved)
    Options:
    This view does not alter the database / create new resources (?)
    """
    context = {}
    context['content'] = request.REQUEST.get("content", "")
    return render_to_response("aawiki/sandbox.html", context, context_instance=RequestContext(request))
