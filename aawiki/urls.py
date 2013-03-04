from django.conf.urls.defaults import include, patterns, url
from django.views.generic.simple import redirect_to
from tastypie.api import Api
from aawiki.api import PageResource, SectionResource


urlpatterns = patterns('aawiki.views',
    url(r'^$', redirect_to, {'url': '/pages/Index'}),
    url(r'^pages/$', redirect_to, {'url': '/pages/Index'}, name='page-index'),
    url(r'^pages/(?P<slug>[^/]+)/$', 'page_detail', {}, name='page-detail'),
    url(r'^pages/(?P<slug>[^/]+)/edit/$', 'page_edit', {}, name='page-edit'),
    url(r'^pages/(?P<slug>[^/]+)/history/$', 'page_history', {}, name='page-history'),
    url(r'^pages/(?P<slug>[^/]+)/diff/$', 'page_diff', {}, name='page-diff'),
    url(r'^pages/(?P<slug>[-\w]+)/flag/$', 'page_flag', {}, name='page-flag'),
    url(r'^upload/$', 'file_upload', {}, name='file-upload'),

    ### Export
    url(r'^pages/(?P<slug>[^/]+)/annotations/(?P<section>\d+)/$', 'annotation_export', 
        {}, name='annotation-export'),
    url(r'^pages/(?P<slug>[^/]+)/annotations/(?P<section>\d+)/import$', 'annotation_import', 
        {}, name='annotation-import'),

    ### EMBED
    url(r'^embed/$', 'embed', {}, name='embed'),

    ### SANDBOX
    url(r'^sandbox/$', 'sandbox', {}, name='sandbox'),
)


v1_api = Api(api_name='v1')
v1_api.register(PageResource())
v1_api.register(SectionResource())

urlpatterns += patterns('',
    (r'^api/', include(v1_api.urls)),
)
