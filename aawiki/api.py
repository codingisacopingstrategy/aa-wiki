"""
========
REST API
========

.. http://127.0.0.1:8000/api/v1/
.. http://127.0.0.1:8000/api/v1/page/
.. http://127.0.0.1:8000/api/v1/page/:name/
.. http://127.0.0.1:8000/api/v1/page/:name/?section=:section
.. http://127.0.0.1:8000/api/v1/page/:name/?format=:format
.. http://127.0.0.1:8000/api/v1/page/:name/section/
.. http://127.0.0.1:8000/api/v1/page/:name/section/:id/
"""


from django.conf.urls.defaults import url
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.bundle import Bundle
from tastypie.exceptions import NotFound
from tastypie.resources import Resource
from tastypie.utils import trailing_slash

import time

from aawiki.mdx.mdx_sectionedit import (sectionalize, sectionalize_replace)
from aawiki.utils import convert_line_endings
from aawiki.settings import REPO_PATH
from pygit2 import GIT_OBJ_BLOB, Repository, Signature

try: import simplejson as json
except ImportError: import json


REPO = Repository(REPO_PATH)


class Section(object):
    def __init__(self, **kwargs): 
        self.__dict__.update(kwargs)


class PageManager(object):
    def get(self, key, hex=None):
        commit = REPO[hex] if hex else REPO.head
        te = commit.tree[key]
        blob = te.to_object()
        content = blob.data.decode("utf-8")
        return Page(name=key, content=content, revision=commit.hex)

    def all(self):
        revision = REPO.head.hex
        for te in REPO.head.tree:
            blob = te.to_object()
            if blob.type == GIT_OBJ_BLOB and not te.name.startswith("."):
                content = blob.data.decode("utf-8")
                yield Page(name=te.name, content=content, revision=revision)


class Page(object):
    objects = PageManager()

    def __getattr__(self, attr):
        if attr == "sections":
            return sectionalize(self.content)
        else:
            raise AttributeError, attr

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name')
        self.content = kwargs.get('content')
        self.revision = kwargs.get('revision')

    def delete(self, message, user, email):
        author = committer = Signature(user, email, time.time(), 0)

        builder = REPO.TreeBuilder(REPO.head.tree)
        builder.remove(self.name)
        tree_oid = builder.write()

        ## commits the changes
        REPO.create_commit('HEAD', author, committer, message, tree_oid, [REPO.head.oid])

    def normalize(self):
        self.content = convert_line_endings(self.content, 0)  # Normalizes EOL
        self.content = self.content.strip() + "\n\n"  # Normalizes whitespace around the markdown

    def commit(self, message, user, email):
        author = committer = Signature(user, email, time.time(), 0)

        blob_oid = REPO.create_blob(self.content.encode("utf-8"))
        builder = REPO.TreeBuilder(REPO.head.tree)
        builder.insert(self.name, blob_oid, 0100644)
        tree_oid = builder.write()

        ## commits the changes
        REPO.create_commit('HEAD', author, committer, message, tree_oid, [REPO.head.oid])


class PageResource(Resource):
    name = fields.CharField(attribute='name')
    content = fields.CharField(attribute='content')
    revision = fields.CharField(attribute='revision', readonly=True)
    
    class Meta:
        resource_name = 'page'
        object_class = Page
        authentication = Authentication()
        authorization = Authorization()

    def base_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^(?P<resource_name>%s)/set/(?P<name_list>\w[\w\.;-]*)/$" % self._meta.resource_name, 
                self.wrap_view('get_multiple'), name="api_get_multiple"),
            url(r"^(?P<resource_name>%s)/(?P<name>\w[\w\.-]*)%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['name'] = bundle_or_obj.obj.name
        else:
            kwargs['name'] = bundle_or_obj.name
        
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name
        
        return self._build_reverse_url('aawiki:api_dispatch_detail', kwargs=kwargs)

    def obj_get_list(self, request=None, **kwargs):
        return [p for p in Page.objects.all()]

    def obj_get(self, request=None, **kwargs):
        hex = request.GET.get('hex') if request else None
        name = kwargs['name']

        try:
            return Page.objects.get(name, hex=hex)
        except KeyError:
            raise NotFound("Object not found") 
    
    def obj_create_or_update(self, bundle, request=None, **kwargs):
        bundle = self.full_hydrate(bundle)

        message = bundle.data.get("message") or "<edited page %s>" % bundle.data['name']
        user = request.user.username if request.user.username else "anonymous"
        email = "%s@%s" % (user, request.META.get('REMOTE_ADDR', "localhost"))
        
        bundle.obj.commit(message=message, user=user, email=email)

        return bundle
    
    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj = Page()

        return self.obj_create_or_update(bundle, request=request)

    def obj_update(self, bundle, request=None, **kwargs):
        bundle.data['name'] = kwargs['name']

        try:
            bundle.obj = Page.objects.get(bundle.data['name'])
        except KeyError:
            raise NotFound("Object not found")  # will call "obj_create"
        
        return self.obj_create_or_update(bundle, request=request)

    def obj_delete(self, request=None, **kwargs):
        name = kwargs.pop('name')

        try:
            page = Page.objects.get(name)
        except KeyError:
            raise NotFound("Object not found") 

        request.DELETE = json.loads(request.raw_post_data)

        message = request.DELETE.get("message") or "<no messages>"
        user = request.user.username if request.user.username else "anonymous"
        email = "%s@%s" % (user, request.META.get('REMOTE_ADDR', "localhost"))
        
        page.delete(message=message, user=user, email=email)


class SectionResource(Resource):
    content = fields.CharField(attribute='content')
    header = fields.CharField(attribute='header', readonly=True)
    body = fields.CharField(attribute='body', readonly=True)
    index = fields.IntegerField(attribute='index', readonly=True)
    start = fields.IntegerField(attribute='start', readonly=True)
    end = fields.IntegerField(attribute='end', readonly=True)

    class Meta:
        resource_name = 'section'
        object_class = Section
        authentication = Authentication()
        authorization = Authorization()

    def base_urls(self):
        return [
            url(r"^page/(?P<parent_name>\w[\w/\.-]*)/(?P<resource_name>%s)%s$" 
                % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^page/(?P<parent_name>\w[\w/\.-]*)/(?P<resource_name>%s)/schema%s$" 
                % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^page/(?P<parent_name>\w[\w/\.-]*)/(?P<resource_name>%s)/set/(?P<pk_list>\d[\d;]*)/$" 
                % self._meta.resource_name, self.wrap_view('get_multiple'), name="api_get_multiple"),
            url(r"^page/(?P<parent_name>\w[\w/\.-]*)/(?P<resource_name>%s)/(?P<pk>\d+)%s$" 
                % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.index
        else:
            kwargs['pk'] = bundle_or_obj.index
        
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name
        
        return self._build_reverse_url('aawiki:api_dispatch_detail', kwargs=kwargs)

    def obj_get_list(self, request=None, **kwargs):
        hex = request.GET.get('hex') if request else None
        name = kwargs.pop('parent_name')

        try:
            page = Page.objects.get(name, hex=hex)
        except KeyError:
            raise NotFound("Object not found") 

        return [Section(**i) for i in sectionalize(page.content)]

    def obj_get(self, request=None, **kwargs):
        hex = request.GET.get('hex') if request else None
        name = kwargs['parent_name']

        try:
            page = Page.objects.get(name, hex=hex)
        except KeyError:
            raise NotFound("Object not found") 

        try:
            section = page.sections[int(kwargs['pk'])]
        except IndexError:
            raise NotFound("Object not found") 

        return Section(**section)

    def obj_create(self, bundle, request=None, **kwargs):
        raise NotImplementedError()

    def obj_update(self, bundle, request=None, **kwargs):
        name = kwargs['parent_name']

        bundle = self.full_hydrate(bundle)

        try:
            page = Page.objects.get(name)
        except KeyError:
            raise NotFound("Object not found") 

        try:
            page.content = sectionalize_replace(page.content, int(kwargs['pk']), bundle.obj.content)
        except IndexError:
            raise NotFound("Object not found") 

        message = bundle.data.get("message") or "<edited page %s>" % name
        user = request.user.username if request.user.username else "anonymous"
        email = "%s@%s" % (user, request.META.get('REMOTE_ADDR', "localhost"))
        
        page.commit(message=message, user=user, email=email)

        return bundle
