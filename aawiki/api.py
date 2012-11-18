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
from tastypie import fields, http
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
from pygit2 import GIT_OBJ_BLOB, GIT_SORT_TIME, Repository, Signature, init_repository

try: import simplejson as json
except ImportError: import json


# a dummy class representing a page of data
class Page(object):
    repo = Repository(REPO_PATH)

    @classmethod
    def get(cls, key, hex=None):
        if hex:
            commit = cls.repo[hex]
        else:
            commit = cls.repo.head
        te = commit.tree[key]
        blob = te.to_object()
        content = blob.data.decode("utf-8")
        return Page(name=key, content=content, revision=commit.hex)

    @classmethod
    def all(cls):
        pages = []
        revision = cls.repo.head.hex
        for te in cls.repo.head.tree:                             
            blob = te.to_object()
            if blob.type == GIT_OBJ_BLOB and not te.name.startswith("."):
                content = blob.data.decode("utf-8")
                pages.append(Page(name=te.name, content=content, revision=revision))
        return pages

    def delete(self,  message, user, email):
        author = committer = Signature(user, email, time.time(), 0)

        builder = Page.repo.TreeBuilder(Page.repo.head.tree)
        builder.remove(self.name)
        tree_oid = builder.write()

        ## commits the changes
        Page.repo.create_commit('HEAD', author, committer, message, tree_oid, [Page.repo.head.oid])

    def normalize(self):
        self.content = convert_line_endings(self.content, 0)  # Normalizes EOL
        self.content = self.content.strip() + "\n\n" # Normalize whitespace around the markdown

    def commit(self, message, user, email):
        author = committer = Signature(user, email, time.time(), 0)

        blob_oid = Page.repo.create_blob(self.content.encode("utf-8"))
        builder = Page.repo.TreeBuilder(Page.repo.head.tree)
        builder.insert(self.name, blob_oid, 0100644)
        tree_oid = builder.write()

        ## commits the changes
        Page.repo.create_commit('HEAD', author, committer, message, tree_oid, [Page.repo.head.oid])
        

    def __init__(self, name=None, content=None, revision=None):
        self.name = name
        self.content = content
        self.revision = revision


class PageResource(Resource):
    # fields must map to the attributes in the Page class
    name = fields.CharField(attribute='name')
    content = fields.CharField(attribute='content')
    revision = fields.CharField(attribute='revision', readonly=True)

    #hex = fields.CharField(attribute='revision', readonly=True)
    #message = fields.CharField(attribute='revision', readonly=True)
    #author = fields.CharField(attribute='revision', readonly=True)
    
    class Meta:
        resource_name = 'page'
        object_class = Page
        authentication = Authentication()
        authorization = Authorization()

    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        # Due to the way Django parses URLs, ``get_multiple`` won't work without
        # a trailing slash.
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

    # adapted this from ModelResource
    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['name'] = bundle_or_obj.obj.name # name is referenced in ModelResource
        else:
            kwargs['name'] = bundle_or_obj.name
        
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name
        
        return self._build_reverse_url('aawiki:api_dispatch_detail', kwargs=kwargs)

    def get_object_list(self, request):
        # inner get of object list... this is where you'll need to
        # fetch the data from what ever data source
        return Page.all()

    def obj_get_list(self, request=None, **kwargs):
        # outer get of object list... this calls get_object_list and
        # could be a point at which additional filtering may be applied
        return self.get_object_list(request)

    def obj_get(self, request=None, **kwargs):
        # get one object from data source
        hex = request.GET.get('hex') if request else None
        name = kwargs['name']

        try:
            return Page.get(name, hex=hex)
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
            bundle.obj = Page.get(bundle.data['name'])
        except KeyError:
            raise NotFound("Object not found")  # will call "obj_create"
        
        return self.obj_create_or_update(bundle, request=request)

    def obj_delete(self, request=None, **kwargs):
        name = kwargs['name']

        try:
            obj = Page.get(name)
        except KeyError:
            raise NotFound("Object not found") 

        #import ipdb; ipdb.set_trace()
        request.DELETE = json.loads(request.raw_post_data)
        message = request.DELETE.get("message") or "<no messages>"
        user = request.user.username if request.user.username else "anonymous"
        email = "%s@%s" % (user, request.META.get('REMOTE_ADDR', "localhost"))
        
        obj.delete(message=message, user=user, email=email)


class SectionObject(object):
    def __init__(self, initial=None):
        self.__dict__['_data'] = {}

        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data


class SectionResource(Resource):
    header = fields.CharField(attribute='header')
    body = fields.CharField(attribute='body')
    index = fields.IntegerField(attribute='index', readonly=True)
    start = fields.IntegerField(attribute='start', readonly=True)
    end = fields.IntegerField(attribute='end', readonly=True)

    class Meta:
        resource_name = 'section'
        object_class = SectionObject
        authentication = Authentication()
        authorization = Authorization()

    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        # Due to the way Django parses URLs, ``get_multiple`` won't work without
        # a trailing slash.
        return [
            url(r"^(?P<parent_resource_name>page)/(?P<parent_name>\w[\w/\.-]*)/(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<parent_resource_name>page)/(?P<parent_name>\w[\w/\.-]*)/(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^(?P<parent_resource_name>page)/(?P<parent_name>\w[\w/\.-]*)/(?P<resource_name>%s)/set/(?P<pk_list>\d[\d;]*)/$" % self._meta.resource_name, self.wrap_view('get_multiple'), name="api_get_multiple"),
            url(r"^(?P<parent_resource_name>page)/(?P<parent_name>\w[\w/\.-]*)/(?P<resource_name>%s)/(?P<pk>\d+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

        ##/pages/Index/sections/
        ##/pages/Index/sections/schema/
        ##/pages/Index/sections/set/1;3
        ##/pages/Index/sections/1/

    # adapted this from ModelResource
    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['name'] = bundle_or_obj.obj.name # name is referenced in ModelResource
        else:
            kwargs['name'] = bundle_or_obj.name
        
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name
        
        return self._build_reverse_url('aawiki:api_dispatch_detail', kwargs=kwargs)

    def get_object_list(self, request, **kwargs):
        name = kwargs['parent_name']

        try:
            page = Page.get(name)
        except KeyError:
            raise NotFound("Object not found") 

        return [SectionObject(i) for i in sectionalize(page.content)]

    def obj_get_list(self, request=None, **kwargs):
        return self.get_object_list(request, **kwargs)

    def obj_get(self, request=None, **kwargs):
        # get one object from data source
        name = kwargs['parent_name']
        try:
            page = Page.get(name)
        except KeyError:
            raise NotFound("Object not found") 

        section = sectionalize(page.content)[int(kwargs['pk'])]
        return SectionObject(section)

    def obj_create(self, bundle, request=None, **kwargs):
        raise NotImplementedError()

    def obj_update(self, bundle, request=None, **kwargs):
        bundle.obj = SectionObject(initial=kwargs)
        bundle = self.full_hydrate(bundle)

        #page = self._meta.queryset.get(name=kwargs['name'])
        page = self._meta.queryset.get(name='Index')
        page.content = sectionalize_replace(page.content, int(kwargs['pk']), "bla")
        page.save()
        return bundle

    #def obj_delete_list(self, request=None, **kwargs):
        #bucket = self._bucket()

        #for key in bucket.get_keys():
            #obj = bucket.get(key)
            #obj.delete()

    #def obj_delete(self, request=None, **kwargs):
        #bucket = self._bucket()
        #obj = bucket.get(kwargs['pk'])
        #obj.delete()

    #def rollback(self, bundles):
        #pass
    def get_multiple(self, request, **kwargs):
        """
        Returns a serialized list of resources based on the identifiers
        from the URL.

        Calls ``obj_get`` to fetch only the objects requested. This method
        only responds to HTTP GET.

        Should return a HttpResponse (200 OK).
        """
        # TODO: implement. Should call obj_get method with kwargs pk and *name*.
        return http.HttpNotImplemented()
