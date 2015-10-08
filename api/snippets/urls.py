from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('snippets.views',
    # url(r'^duplicated/(?P<filters>(?:\w+/)+)', 'snippet_list'),
    url(r'^duplicated/aviso/(?P<id>[^\?]+)/$', 'snippet_detail'),
    url(r'^api/duplicated/(?P<filters>(?:\w+/)+)', 'snippet_list_api'),
    url(r'^duplicated/filtered/$', 'equals_ads_list_filtered'),
    url(r'^duplicated/grouped/$', 'equals_ads_list_filtered_grouped'),
    url(r'^api/aviso/duplicated/(?P<id>[^\?]+)/$', 'snippet_detail_api'),
    url(r'^redirect_to_aviso/(?P<id>[^\?]+)/$', 'redirect_to_aviso'),
    url(r'^group/$', 'get_group_number_of_ads'),
    url(r'^filtered/$', 'get_group_number_of_ads_filtered'),
    url(r'^virtual-tour/$', 'go_to_virtual_tour'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)