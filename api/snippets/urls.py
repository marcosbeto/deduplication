from django.conf.urls import patterns, url

urlpatterns = patterns('snippets.views',
    url(r'^duplicated/all$', 'snippet_list'),
    url(r'^duplicated/aviso/(?P<id>[^\?]+)/$', 'snippet_detail'),
    url(r'^duplicated/api/all/$', 'snippet_list_api'),
    url(r'^duplicated/api/aviso/(?P<id>[^\?]+)/$', 'snippet_detail_api'),
    url(r'^redirect_to_aviso/(?P<id>[^\?]+)/$', 'redirect_to_aviso'),
)