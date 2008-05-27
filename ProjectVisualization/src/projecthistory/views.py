from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson
from datetime import date, timedelta
from projecthistory import models

def stats(request):
    stats = [(str(s.date), s.log_normal_count) for s in models.DailyStats.objects.all()]
    return HttpResponse(simplejson.dumps(stats))
