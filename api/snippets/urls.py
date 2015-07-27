from django.conf.urls import patterns, url

urlpatterns = patterns('snippets.views',
    url(r'^snippets/$', 'snippet_list'),
    url(r'^snippets/(?P<id>[^\?]+)/$', 'snippet_detail'),
    url(r'^redirect_to_aviso/(?P<id>[^\?]+)/$', 'redirect_to_aviso'),
)