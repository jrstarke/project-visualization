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
    return selectedstats(request,'0','0')

def selectedstats(request, author_id_str, module_id_str):
    author_id = int(author_id_str)
    module_id = int(module_id_str)
    return HttpResponse(simplejson.dumps(models.selectedstats(author_id,module_id)))

# returns a list of events for the given day
def events(request, date_str):
     return eventrange(request, date_str, date_str)

def eventrange(request, date_str_start, date_str_stop):
    #return all events for the range, where we don't care about who the author or module are (= 0)
    return selectedeventrange(request, date_str_start, date_str_stop, '0', '0')

def selectedeventrange(request, date_str_start, date_str_stop, author_id_str, module_id_str):
    start = parse_date(date_str_start)
    stop = parse_date(date_str_stop) + timedelta(1)
    author_id = int(author_id_str)
    module_id = int(module_id_str)
    files = {}
    status = {}
    modules = {}
    
    for p in models.Path.objects.all():
        if not files.setdefault(p.event_id,[]).__contains__(p.dest_file):
            files[p.event_id].append(p.dest_file)
            status.setdefault(p.event_id,[]).append(p.action)

        if not modules.setdefault(p.event_id,[]).__contains__(p.module_id):
            modules[p.event_id].append(p.module_id) 
    all_events = []
    for event in models.events(start,stop,author_id,module_id):
        all_events.append({'date':str(event.date)[:str(event.date).rfind(" ")], 'author_short_name':models.authorshortname(event.author.name),
                   'pk':event.id, 'comment':event.comment, 'author':event.author.id, 'author_name':event.author.name,
                   'modules':modules.get(event.id,[]),'files':files.get(event.id,[]), 'status':status.get(event.id,[])}) 
                   
    return HttpResponse(simplejson.dumps(all_events))

def topauthors(request, start_date, end_date, num_authors):
   #start = parse_date(start_date)
   #end = parse_date(end_date) + timedelta(1)
   start = date(2006,01,01)
   end = date(2007,12,31) + timedelta(1)
   number = int(num_authors)
   all_events = models.topauthors(start, end, number)
   return HttpResponse(simplejson.dumps(all_events))
   #return HttpResponse(start_date + " " + end_date + " " + num_authors)

def topauthorsfordays(request):
    models.topauthorsfordays()
    return HttpResponse("read stuff")

def modules(request):
    modules = models.modules()
    return HttpResponse(simplejson.dumps(modules))

def filesinmodule(request, module_id_str):
    module_id = int(module_id_str)
    files = models.files_in_module(module_id)
    return HttpResponse(simplejson.dumps(files))

def cross_domain(request):
    return HttpResponse('''
    <?xml version="1.0"?>
   <!DOCTYPE cross-domain-policy SYSTEM "http://www.macromedia.com/xml/dtds/cross-domain-policy.dtd">
   <cross-domain-policy>
   <allow-access-from domain="*" />
   </cross-domain-policy>
    ''')