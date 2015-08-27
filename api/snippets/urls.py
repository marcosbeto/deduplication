from django.conf.urls import patterns, url

urlpatterns = patterns('snippets.views',
    # url(r'^duplicated/(?P<filters>(?:\w+/)+)', 'snippet_list'),
    url(r'^duplicated/aviso/(?P<id>[^\?]+)/$', 'snippet_detail'),
    url(r'^api/duplicated/(?P<filters>(?:\w+/)+)', 'snippet_list_api'),
    url(r'^duplicated/filtered/$', 'equals_ads_list_filtered'),
    url(r'^duplicated/grouped/$', 'equals_ads_list_filtered_grouped'),
    url(r'^api/duplicated/aviso/(?P<id>[^\?]+)/$', 'snippet_detail_api'),
    url(r'^redirect_to_aviso/(?P<id>[^\?]+)/$', 'redirect_to_aviso'),
    url(r'^group/$', 'get_group_number_of_ads'),
    url(r'^filtered/$', 'get_group_number_of_ads_filtered'),
)