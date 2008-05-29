from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^stats/$', 'projecthistory.views.stats'),
    (r'^events/(?P<date_str>[\d-]+)/$', 'projecthistory.views.events'),
    (r'^crossdomain.xml', 'projecthistory.views.cross_domain'),    
)
