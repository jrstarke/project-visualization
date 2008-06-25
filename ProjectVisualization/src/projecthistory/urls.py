from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^stats/$', 'projecthistory.views.stats'),
    (r'^events/(?P<date_str>[\d-]+)/$', 'projecthistory.views.events'),
    (r'^eventsrange/(?P<date_str_start>[\d-]+)/(?P<date_str_stop>[\d-]+)/$', 'projecthistory.views.eventrange'),
    (r'^topauthors/(?P<start_date>[\d-]+)/(?P<end_date>[\d-]+)/(?P<num_authors>\d+)/$', 'projecthistory.views.topauthors'),
    (r'^topauthorsfordays/', 'projecthistory.views.topauthorsfordays'),
    (r'^modules/$', 'projecthistory.views.modules'),
    (r'^filesinmodule/(?P<module_id_str>[\d-]+)/$', 'projecthistory.views.filesinmodule'),
    (r'^crossdomain.xml', 'projecthistory.views.cross_domain'),    
)
