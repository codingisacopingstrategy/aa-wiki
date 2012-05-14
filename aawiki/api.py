from tastypie import http
from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.utils import trailing_slash
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import (ModelResource, Resource)
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from aawiki.models import Page
import csv
import StringIO
from tastypie.serializers import Serializer
from audacity import srt_to_audacity
from django.conf.urls.defaults import url
from aawiki.mdx.mdx_sectionedit import (sectionalize, sectionalize_replace)
from tastypie.validation import Validation


class CustomAuthentication(BasicAuthentication):
    def is_authenticated(self, request, **kwargs):
        if request.method in ('GET', 'OPTIONS', 'HEAD'):
            return True
        else:
            return super(CustomAuthentication, self).is_authenticated(request, **kwargs)


class PageResource(ModelResource):
    class Meta:
        queryset = Page.objects.all()
        resource_name = 'page'
        authentication = CustomAuthentication()
        authorization = DjangoAuthorization()
        include_resource_uri = False
        #excludes = ['id']

    #def get_resource_uri(self, bundle_or_obj):
        #"""
        #Handles generating a resource URI for a single resource.

        #Uses the model's ``pk`` in order to create the URI.
        #"""
        #kwargs = {
            #'resource_name': self._meta.resource_name,
        #}

        #if isinstance(bundle_or_obj, Bundle):
            #kwargs['name'] = bundle_or_obj.obj.name
        #else:
            #kwargs['name'] = bundle_or_obj.name

        #if self._meta.api_name is not None:
            #kwargs['api_name'] = self._meta.api_name

        #return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)


    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        # Due to the way Django parses URLs, ``get_multiple`` won't work without
        # a trailing slash.
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
            #url(r"^(?P<resource_name>%s)/set/(?P<pk_list>[-\w;-]+)/$" % self._meta.resource_name, self.wrap_view('get_multiple'), name="api_get_multiple"),
            url(r"^(?P<resource_name>%s)/(?P<pk>[-\w]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    #def override_urls(self):
        #return [
            ##url(r"^(?P<resource_name>%ss)%s$" % (self._meta.resource_name, trailing_slash()), 
                ##self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            ##url(r"^(?P<resource_name>%ss)/schema%s$" % (self._meta.resource_name, trailing_slash()), 
                ##self.wrap_view('get_schema'), name="api_get_schema"),
            ##url(r"^(?P<resource_name>%ss)/set/(?P<pk_list>\w[\w/;-]*)/$" % self._meta.resource_name, 
                ##self.wrap_view('get_multiple'), name="api_get_multiple"),
            #url(r"^(?P<resource_name>%ss)/(?P<name>[-\w]+)%s$" % (self._meta.resource_name, 
                #trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        #]

    #def dehydrate(self, bundle):
        ## Include the request IP in the bundle.
        #section = int(bundle.request.GET.get('section', 0))
        #s = sectionalize(bundle.data['content'])[section]
        #bundle.data['content'] = s['header'] + s['body']
        #return bundle


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
        #queryset = Page.objects.all()
        resource_name = 'section'
        object_class = SectionObject
        authentication = CustomAuthentication()
        authorization = DjangoAuthorization()
        #include_resource_uri = False
        #excludes = ['id']

    def override_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        # Due to the way Django parses URLs, ``get_multiple`` won't work without
        # a trailing slash.
        return [
            url(r"^page/(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^page/(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^page/(?P<resource_name>%s)/set/(?P<pk_list>\w[\w/;-]*)/$" % self._meta.resource_name, self.wrap_view('get_multiple'), name="api_get_multiple"),
            url(r"^page/(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
        ##/pages/Index/sections/
        ##/pages/Index/sections/schema/
        ##/pages/Index/sections/set/1;3
        ##/pages/Index/sections/1/
        #return [
            #url(r"^(?P<resource_name>%s)s/(?P<name>[-\w]+)/sections%s$" % (self._meta.resource_name, trailing_slash()), 
                #self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            #url(r"^(?P<resource_name>%s)s/(?P<name>[-\w]+)/sections/schema%s$" % (self._meta.resource_name, trailing_slash()), 
                #self.wrap_view('get_schema'), name="api_get_schema"),
            #url(r"^(?P<resource_name>%s)s/(?P<name>[-\w]+)/sections/set/(?P<pk_list>\d+[;-]\d+)%s$" % (self._meta.resource_name, trailing_slash()),
                #self.wrap_view('get_multiple'), name="api_get_multiple"),
            #url(r"^(?P<resource_name>%s)s/(?P<name>[-\w]+)/sections/(?P<pk>\d+)%s$" % (self._meta.resource_name,
                #trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        #]

    def get_resource_uri(self, bundle_or_obj):
        """
        Handles generating a resource URI for a single resource.
        """
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['name'] = bundle_or_obj.obj.name
        else:
            kwargs['name'] = bundle_or_obj.name

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)

    def get_object_list(self, request, **kwargs):
        page = self._meta.queryset.get(name=kwargs['name'])
        return [SectionObject(i) for i in sectionalize(page.content)]

    def obj_get_list(self, request=None, **kwargs):
        # Filtering disabled for brevity...
        import pdb; pdb.set_trace()
        return self.get_object_list(request, **kwargs)

    def obj_get(self, request=None, **kwargs):
        page = self._meta.queryset.get(name=kwargs['name'])
        section = sectionalize(page.content)[int(kwargs['pk'])]
        return SectionObject(section)

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj = SectionObject(initial=kwargs)
        bundle = self.full_hydrate(bundle)

        #page = self._meta.queryset.get(name=kwargs['name'])
        page = self._meta.queryset.get(name='Index')
        page.content = sectionalize_replace(page.content, int(kwargs['pk']), "bla")
        page.save()
        
        
        #page = self._meta.queryset.get(name=kwargs['name'])

        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        return self.obj_create(bundle, request, **kwargs)

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
