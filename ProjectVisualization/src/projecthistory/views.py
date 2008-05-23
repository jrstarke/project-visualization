from django.http import HttpResponseRedirect, HttpResponse
#from django.core import serializers
from django.utils import simplejson
from datetime import date, timedelta
from projecthistory import models

#def tojson(obj):
#    return serializers.serialize("json", obj)

def stats(request):
    stats = [(str(s.date), s.commit_events, s.new_ticket_events, s.ticket_change_events)
        for s in models.DailyStats.objects.all()]
    return HttpResponse(simplejson.dumps(stats))
