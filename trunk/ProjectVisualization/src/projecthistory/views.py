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
  
    all_events = []
    for event in models.events(date,next):
        files = []
        modules = []
        new_status = ""
        if event.__class__.__name__ == 'CommitEvent':
            for p in event.path_set.all():
                if not files.__contains__(p.dest_file):   
                    files.append(p.dest_file)
                if (not modules.__contains__(p.module.id)):
                    modules.append(p.module.id)
        if event.__class__.__name__ == 'NewTicketEvent':
            new_status = 'new'           
        if event.__class__.__name__ == 'TicketChangeEvent':
            for tc in event.ticketchange_set.all():
                if tc.changed_field == "status":
                  new_status = tc.to_value          
        all_events.append({'date':str(event.date)[:str(event.date).rfind(" ")], 'author_short_name':models.authorshortname(event.author.name),
                   'pk':event.id, 'comment':event.comment, 'author':event.author.id, 'author_name':event.author.name,
                   'type':event.__class__.__name__.replace('Event', ''), 'files':files, 'modules':modules, 'new_status':new_status}) 
        
    #return HttpResponse(serializers.serialize('json', iter(all_events)))
    return HttpResponse(simplejson.dumps(all_events))

def eventrange(request, date_str_start, date_str_stop):
    start = parse_date(date_str_start)
    stop = parse_date(date_str_stop) + timedelta(1)
    #all_events = models.events(date, next)
    
    all_events = []
    for event in models.events(start,stop):
        files = []
        modules = []
        new_status = ""
        if event.__class__.__name__ == 'CommitEvent':
            for p in event.path_set.all():
                if not files.__contains__(p.dest_file):   
                    files.append(p.dest_file)
                if (not modules.__contains__(p.module.id)):
                    modules.append(p.module.id)
        if event.__class__.__name__ == 'NewTicketEvent':
            new_status = 'new'           
        if event.__class__.__name__ == 'TicketChangeEvent':
            for tc in event.ticketchange_set.all():
                  new_status = tc.to_value          
        all_events.append({'date':str(event.date)[:str(event.date).rfind(" ")], 'author_short_name':models.authorshortname(event.author.name),
                   'pk':event.id, 'comment':event.comment, 'author':event.author.id, 'author_name':event.author.name,
                   'type':event.__class__.__name__.replace('Event', ''), 'files':files, 'modules':modules, 'new_status':new_status}) 
                   
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