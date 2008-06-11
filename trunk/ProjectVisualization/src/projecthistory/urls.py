from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^stats/$', 'projecthistory.views.stats'),
    (r'^events/(?P<date_str>[\d-]+)/$', 'projecthistory.views.events'),
    (r'^topauthors/(?P<start_date>[\d-]+)/(?P<end_date>[\d-]+)/(?P<num_authors>\d+)/$', 'projecthistory.views.topauthors'),
    (r'^topauthorsfordays/', 'projecthistory.views.topauthorsfordays'),
    (r'^crossdomain.xml', 'projecthistory.views.cross_domain'),    
)
