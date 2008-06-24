from django.http import HttpResponseRedirect, HttpResponse
from django.core import serializers
from django.utils import simplejson
from datetime import date, timedelta
from time import strptime
from projecthistory import models

def parse_date(date_str):
    date_str = date_str[:19]
    return date(*strptime(date_str, '%Y-%m-%d')[0:3])

def stats(request):
    stats = [(str(s.date), s.log_normal_count) for s in models.DailyStats.objects.all()]
    return HttpResponse(simplejson.dumps(stats))

# returns a list of events for the given day
def events(request, date_str):
    date = parse_date(date_str)
    next = date + timedelta(1)
    #all_events = models.events(date, next)
    
    all_events = [{'date':str(event.date)[:str(event.date).rfind(" ")], 'author_short_name':models.authorshortname(event.author.name),
                   'pk':event.id, 'comment':event.comment, 'author':event.author.id, 'author_name':event.author.name,
                   'type':event.__class__.__name__.replace('Event', '')} 
                   for event in models.events(date, next)]
        
    #return HttpResponse(serializers.serialize('json', iter(all_events)))
    return HttpResponse(simplejson.dumps(all_events))

def topauthors(request, start_date, end_date, num_authors):
   start = parse_date(start_date)
   end = parse_date(end_date) + timedelta(1)
   number = int(num_authors)
   all_events = models.topauthors(start, end, number)
   return HttpResponse(simplejson.dumps(all_events))
   #return HttpResponse(start_date + " " + end_date + " " + num_authors)

def topauthorsfordays(request):
    models.topauthorsfordays()
    return HttpResponse("read stuff")

def cross_domain(request):
    return HttpResponse('''
    <?xml version="1.0"?>
   <!DOCTYPE cross-domain-policy SYSTEM "http://www.macromedia.com/xml/dtds/cross-domain-policy.dtd">
   <cross-domain-policy>
   <allow-access-from domain="*" />
   </cross-domain-policy>
    ''')