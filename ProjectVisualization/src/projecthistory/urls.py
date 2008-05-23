from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^stats/', 'projecthistory.views.stats'),
)
