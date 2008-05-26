from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^stats/', 'projecthistory.views.stats'),
    (r'^crossdomain.xml', 'projecthistory.views.cross_domain'),    
)
