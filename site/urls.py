# -*- encoding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.conf import settings
from filebrowser.sites import site as fb_site

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'www.views.index', name='index'),	
    url(r'^search/$', 'www.views.search', name='search'),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/filebrowser/', include(fb_site.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<path>.*)/$', 'www.views.page', name='page'),
    
)

handler404 = 'www.views.error'
