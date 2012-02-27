from django.conf.urls.defaults import *
from django.views.generic.simple import (redirect_to, direct_to_template)


urlpatterns = patterns('aawiki.views',
    url(r'^$', 'index', {}, 'aa-index'),
    url(r'^pages/$', 'index'),
    url(r'^pages/(?P<slug>[^/]+)/$', 'page_detail', {}, name='aa-page-detail'),
    url(r'^pages/(?P<slug>[^/]+)/edit/$', 'page_edit', {}, name='aa-page-edit'),
    url(r'^pages/(?P<slug>[-\w]+)/history/$', 'page_history', {}, name='aa-page-history'),
    url(r'^pages/(?P<slug>[-\w]+)/diff/$', 'page_diff', {}, name='aa-page-diff'),
    url(r'^pages/(?P<slug>[-\w]+)/flag/$', 'page_flag', {}, name='aa-page-flag'),

    ### Export
    url(r'^pages/(?P<slug>[^/]+)/annotations/(?P<section>\d+)/$', 'annotation_export', 
        {}, name='aa-annotation-export'),
    url(r'^pages/(?P<slug>[^/]+)/annotations/(?P<section>\d+)/import$', 'annotation_import', 
        {}, name='aa-annotation-import'),

    ### EMBED
    url(r'^embed/$', 'embed', {}, name='aa-embed'),

    ### SANDBOX
    url(r'^sandbox/$', 'sandbox', {}, name='aa-sandbox'),
)

### LOGIN ###
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^accounts/login/$', 'login', {'template_name': 'aawiki/login.html'}, name='aa-login'),
    url(r'^accounts/logout/$', 'logout', {'template_name': 'aawiki/logout.html'}, name='aa-logout'),
)
