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
from tastypie.resources import Resource, convert_post_to_patch, dict_strip_unicode_keys, http
from tastypie.utils import trailing_slash

import time

from aawiki.mdx import get_markdown
from aawiki.mdx.mdx_sectionedit import (sectionalize, sectionalize_replace)
from aawiki.utils import convert_line_endings
from aawiki.settings import REPO_PATH
from pygit2 import GIT_OBJ_BLOB, Repository, Signature

try: import simplejson as json
except ImportError: import json

from markdown.extensions.attr_list import get_attrs
from markdown.extensions.attr_list import AttrListTreeprocessor
from markdown.util import etree


REPO = Repository(REPO_PATH)

def assign_attrs(elem, attrs):
    """ Assign attrs to element. """
    for k, v in get_attrs(attrs):
        if k == '.':
            # add to class
            cls = elem.get('class')
            if cls:
                elem.set('class', '%s %s' % (cls, v))
            else:
                elem.set('class', v)
        else:
            # assing attr k with v
            elem.set(k, v)

def add_attributes_key (x):
    if not x["index"] == 0:
        RE = AttrListTreeprocessor.HEADER_RE
        m = list(RE.finditer(x['header'].rstrip()))
        if m:
            elt = etree.Element('tmp')
            assign_attrs(elt, m[-1].group(1))
            x['attributes'] = elt.attrib
    return x


def add_html_key (x):
    if x["index"] == 0:
        md = get_markdown()
    else:
        md = get_markdown(simple=True)
    x['html'] = md.convert(x['content'])
    return x


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
    header = fields.CharField(attribute='header', readonly=True, null=True)
    body = fields.CharField(attribute='body', readonly=True, null=True)
    index = fields.IntegerField(attribute='index', readonly=True)
    start = fields.IntegerField(attribute='start', readonly=True, null=True)
    end = fields.IntegerField(attribute='end', readonly=True, null=True)
    html = fields.CharField(attribute='html', readonly=True, null=True)
    attributes = fields.DictField(attribute='attributes', readonly=True, null=True)

    class Meta:
        resource_name = 'section'
        object_class = Section
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True

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

    def hydrate(self, bundle):
        md = get_markdown(simple=True)
        #import ipdb; ipdb.set_trace()
        bundle.data['html'] = md.convert(bundle.data['content'])
        return bundle

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

        sections = map(add_html_key, sectionalize(page.content))

        return [Section(**i) for i in sections]

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

        return Section(**add_attributes_key(add_html_key(section)))

    def obj_create(self, bundle, request=None, **kwargs):
        raise NotImplementedError()


    def patch_detail(self, request, **kwargs):
        """
        Updates a resource in-place.

        Calls ``obj_update``.

        If the resource is updated, return ``HttpAccepted`` (202 Accepted).
        If the resource did not exist, return ``HttpNotFound`` (404 Not Found).
        """
        request = convert_post_to_patch(request)

        # We want to be able to validate the update, but we can't just pass
        # the partial data into the validator since all data needs to be
        # present. Instead, we basically simulate a PUT by pulling out the
        # original data and updating it in-place.
        # So first pull out the original object. This is essentially
        # ``get_detail``.
        try:
            obj = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle)
        bundle = self.alter_detail_data_to_serialize(request, bundle)

        # Now update the bundle in-place.
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        self.update_in_place(request, bundle, deserialized, **kwargs)
        return http.HttpAccepted()

    def update_in_place(self, request, original_bundle, new_data, **kwargs):
        """
        Update the object in original_bundle in-place using new_data.
        """
        print("fookwargs", kwargs['pk'])
        original_bundle.data.update(**dict_strip_unicode_keys(new_data))

        # Now we've got a bundle with the new data sitting in it and we're
        # we're basically in the same spot as a PUT request. SO the rest of this
        # function is cribbed from put_detail.
        self.alter_deserialized_detail_data(request, original_bundle.data)
        self.is_valid(original_bundle, request)

        return self.obj_update(original_bundle, request=request, **kwargs)

    def obj_update(self, bundle, request=None, **kwargs):
        #import ipdb; ipdb.set_trace()
        name = kwargs['parent_name']

        bundle = self.full_hydrate(bundle)

        if "attributes" in bundle.data:
            attr = "{: "
            for i in bundle.data['attributes']:
                if bundle.data['attributes'][i]:
                    attr += i + '="' + bundle.data['attributes'][i] + '" '
            attr += "}"
            bundle.obj.content = bundle.obj.header.split("{:")[0] + attr + bundle.obj.body




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

        if self.Meta.always_return_data:
            bundle.obj.index = int(kwargs["pk"])
            md = get_markdown(simple=False)
            bundle.obj.html = md.convert(bundle.obj.content)

        return bundle
