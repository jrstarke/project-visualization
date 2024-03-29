import os, re, datetime
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.db import models, connection
from datetime import timedelta, date
import math

class Component(models.Model):
    name = models.TextField()
    
    component_names = ('Admin interface',
        'django-admin.py', 
        'django-admin.py runserver',
        'django-admin.py inspectdb',
        'django.contrib.comments',
        'django.contrib.databrowse', 
        'django.contrib.formtools',
        'django.contrib.localflavor', 
        'django.contrib.sessions',
        'Contrib apps', 
        'Cache system', 
        'Core framework', 
        'django.core.mail',
        'Database wrapper', 
        'django.newforms', 
        'Django Web site', 
        'Documentation',
        'Generic views', 
        'GIS', 
        'HTTP handling', 
        'Internationalization',
        'Metasystem', 
        'RSS framework', 
        'Serialization', 
        'Template system',
        'Tools', 
        'Translations', 
        'Uncategorized', 
        'Unit test system',
        'Validators',)
    
    @classmethod
    def names(cls):
        return [component.name for component in cls.objects.all()]
    
    @classmethod
    def load_defaults(cls):
        for name in cls.component_names:
            cls.objects.get_or_create(name=name.lower())
    
    # returns a component with the given name (newly created if it did
    # not already exist)
    @classmethod
    def by_name(cls, name):
        return cls.objects.get_or_create(name=name.lower())[0]
    
class Author(models.Model):
    name = models.CharField(maxlength=75, unique=True)
    
    # returns an author, possibly newly created
    @classmethod
    def from_string(cls, string):
        string = string.replace('&lt;','').replace('&gt;','').strip()
        return cls.objects.get_or_create(name=string)[0]
    
    #def short_name(self):
    #    return self.name

class Ticket(models.Model):
    open_date = models.DateTimeField(null=True)
    last_mod_date = models.DateTimeField(null=True)
    summary = models.TextField()
    reporter = models.TextField()
    owner = models.ForeignKey(Author)
    description = models.TextField()
    status = models.TextField()
    component = models.ForeignKey(Component)
    version = models.TextField()
    resolution = models.TextField()
    keywords = models.TextField()
    cc = models.TextField()
    stage = models.TextField()
    has_patch = models.BooleanField()
    needs_docs = models.BooleanField()
    needs_tests = models.BooleanField()
    needs_better_patch = models.BooleanField()
    
    def event_set(self):
        return self.ticketchangeevent_set

class Module(models.Model):
    directory = models.TextField(maxlength=150)
    
    dirs = (
        '/django/contrib/admin/', '/django/contrib/comments',
        '/django/contrib/databrowse/', '/django/contrib/formtools/', 
        '/django/contrib/localflavor/', '/django/contrib/sessions/',
        '/django/contrib/', '/django/conf/locale', '/django/conf/',
        '/django/core/serializers/', '/django/core/cache', '/django/core/mail', 
        '/django/core/validators', 
        'django/core/management/commands/', '/django/core/', 
        '/django/db/', '/django/dispatch/', '/django/http/', 
        'django/utils/cache', '/django/middleware/cache', '/django/middleware/', 
         '/django/forms/', '/django/newforms/', '/django/oldforms/',
        '/django/shortcuts/', '/django/template/', '/django/templatetags/', 
        '/django/test/', 
        '/django/utils/feedgenerator', '/django/utils/', 
        '/django/views/generic/', '/django/views/', '/django/',
        '/docs/', '/examples/', '/tests/modeltests/', '/tests/templates/', 
        '/tests/', '/')
    
    @classmethod
    def load(cls):
        for d in cls.dirs:
            cls.objects.get_or_create(directory=d)
    
    # returns the module that is the most specific match to the 
    # given path
    @classmethod
    def from_path(cls, full_path):
        full_path = '/'.join(full_path.split('/')[1:])
        for d in cls.dirs:
            if full_path.find(d) != -1:
                return cls.objects.get(directory=d)
   
class Path(models.Model):
    ACTION_TYPE = (('A', 'added'), ('M', 'modified'),('D', 'deleted'))
    event = models.ForeignKey('CommitEvent')
    action = models.CharField(maxlength=1, choices=ACTION_TYPE)
    dest_file = models.CharField(maxlength=200)
    src_file = models.CharField(maxlength=200, null=True)
    src_revision = models.IntegerField(null=True)
    module = models.ForeignKey(Module)

# -------------------------------------------------------------------

class CommitEvent(models.Model):
    author = models.ForeignKey(Author)
    date = models.DateTimeField()
    lines = models.IntegerField()
    message = models.TextField(null=True)
    def _comment(self):
        return self.message
    comment = property(_comment,None)
    
    # returns a list of components affected by this event
    def modules(self):
        return [p.module for p in self.path_set.all()]

    class Meta:
        ordering = ['date']

class NewTicketEvent(models.Model):
    author = models.ForeignKey(Author) # initial owner
    date = models.DateTimeField()
    ticket = models.ForeignKey(Ticket, unique=True)
    def _comment(self):
        return self.ticket.summary
    comment = property(_comment,None)

    class Meta:
        ordering = ['date']
        
# this is separate from the Change model class, because one event can 
# comprise multiple changes
class TicketChangeEvent(models.Model):
    author = models.ForeignKey(Author)
    date = models.DateTimeField()
    ticket = models.ForeignKey(Ticket)
    comment = models.TextField()
    
    # returns a list of components affected by this event
    def components(self):
        return [self.ticket.component]
        
    class Meta:
        ordering = ['date']
  
class TicketChange(models.Model):
    event = models.ForeignKey(TicketChangeEvent)
    changed_field = models.TextField(null=True)
    from_value = models.TextField(null=True)
    to_value = models.TextField(null=True)
    file_name = models.CharField(maxlength=200, null=True) # for attachments

    def isattachment(self):
        return self.file_name != None
        
class DailyStats(models.Model):
    date = models.DateField(unique=True)
    commit_events = models.IntegerField()
    new_ticket_events = models.IntegerField()
    ticket_change_events = models.IntegerField()
    total_count = models.IntegerField()
    log_normal_count = models.FloatField()
        
    class Meta:
        ordering = ['date']

# returns the number of events of the given type for the given time period
def count_events(start, stop, models=[CommitEvent,NewTicketEvent,TicketChangeEvent]):
    return [m.objects.filter(date__range=(start,stop)).count() for m in models]

def events(start, stop, author_id=0, module_id=0):
    #all_events = _events(start,stop, CommitEvent)
    #all_events = _events(start,stop, NewTicketEvent) + \
    #    _events(start,stop, CommitEvent) + \
    #    _events(start, stop, TicketChangeEvent)
    # should really be merging these ...
    
    ## it was redundant to sort, since we now are getting a sorted list
    #all_events.sort(lambda a,b: cmp(a.date, b.date))
    #for e in all_events:
    #    e["fields"]["author_shortname"] = authorshortname(e["fields"]["author"])
    #return all_events
    if author_id == 0 and module_id == 0:
        return list(CommitEvent.objects.select_related().filter(date__range=(start, stop)).order_by('date'))
    if module_id == 0:
        return list(CommitEvent.objects.select_related().filter(date__range=(start, stop),author__exact=author_id).order_by('date'))    
    if author_id == 0:
        return list(CommitEvent.objects.extra(where=['projecthistory_commitevent.id IN (SELECT projecthistory_path.event_id from projecthistory_path where projecthistory_path.module_id = ' + str(module_id)+ ')']).select_related().filter(date__range=(start, stop)).order_by('date'))
    else:
        return list(CommitEvent.objects.extra(where=['projecthistory_commitevent.id IN (SELECT projecthistory_path.event_id from projecthistory_path where projecthistory_path.module_id = ' + str(module_id)+ ')']).select_related().filter(date__range=(start, stop),author__exact=author_id).order_by('date'))
    
def _events(start, stop, model):
    return list(model.objects.select_related().filter(date__range=(start, stop)).order_by('date'))

def topauthors(start, stop, num_authors):
    cursor = connection.cursor()
    cursor.execute("SELECT DATE(MAX(date)) from projecthistory_commitevent")
    stop = cursor.fetchone()[0]
    #stop = date(2008, 8, 1)
    start = d = stop - timedelta(730)
    
    author_counts = {}
    cursor = connection.cursor()
    cursor.execute("select distinct(a.id) from projecthistory_author as a, projecthistory_commitevent as c where c.author_id = a.id")
#    for a in [Author.objects.get(pk=i) for i in [7,5,3,4,21,10,14,19,12,11,1,6,9,18,16,17,2,20,13,15,8]]:
    for a in [Author.objects.get(pk=i) for i in [x[0] for x in cursor.fetchall()]]:
        author_counts[a.id] = (a.newticketevent_set.filter(date__range=(start,stop)).count(),a.commitevent_set.filter(date__range=(start,stop)).count(),a.ticketchangeevent_set.filter(date__range=(start,stop)).count())
    sorted_counts = author_counts.items()
    sorted_counts.sort(lambda a,b: cmp(b[1][1], a[1][1]))
    top_authors = []
    for i in sorted_counts[:num_authors]:
        author = {}
        author["author"] = i[0]
        author["newticketevents"] = i[1][0]
        author["commitevents"] = i[1][1]
        author["ticketchangeevents"] = i[1][2]
        author["author_name"] = Author.objects.get(pk=i[0]).name
        author["author_shortname"] = authorshortname(author["author_name"])
        top_authors.append(author)
    top_authors.sort(lambda a,b: cmp(a["author_name"].lower(),b["author_name"].lower()))
    #top_authors = filter(lambda x: (x["newticketevents"] + x["commitevents"] + x["ticketchangeevents"]) > 0, top_authors)
    top_authors = filter(lambda x: x["commitevents"] > 0, top_authors)
    return top_authors

def modules():
    modules = []
    for m in Module.objects.all():
        aModule = {}
        aModule["name"] = m.directory
        aModule["pk"] = m.id
        modules.append(aModule)
    modules.sort(lambda a,b: cmp(a['name'],b['name']))
    return modules

def files_in_module(module_id):
    files = []
    module = Module.objects.get(id=module_id)
    for p in module.path_set.all():
        name = p.dest_file[p.dest_file.rfind("/")+1:]
        if not files.__contains__(name):
            files.append(name)
    return files           

def selectedstats(author_id, module_id):
    # start = d = date(2006,01,01) # hard coded dates for now
    cursor = connection.cursor()
    cursor.execute("SELECT DATE(MAX(date)) from projecthistory_commitevent")
    stop = cursor.fetchone()[0]
    #stop = date(2008, 8, 1)
    start = d = stop - timedelta(730)

    cursor = connection.cursor()
    cursor.execute("SELECT MAX(days.daycount) from ( select DATE(c.date), count(distinct c.id) as daycount from projecthistory_commitevent as c where c.date >= '" + str(start) + "' and c.date < '" + str(stop) + "' group by DATE(c.date)) as days")
    max = cursor.fetchone()[0]
    if not (author_id == 0 or module_id == 0): #neither is 0
        cursor.execute("select DATE(c.date), count(distinct c.id) from projecthistory_commitevent as c, projecthistory_path as p where c.date >= '" + str(start) + "' and c.date < '" + str(stop) + "' and c.author_id = " + str(author_id) + " and p.module_id = " + str(module_id) + " and p.event_id = c.id group by DATE(c.date) order by c.date")
    elif not author_id == 0:
        cursor.execute("select DATE(c.date), count(distinct c.id) from projecthistory_commitevent as c where c.date >= '" + str(start) + "' and c.date < '" + str(stop) + "' and c.author_id = " + str(author_id) + " group by DATE(c.date) order by c.date")
    elif not module_id == 0:
        cursor.execute("select DATE(c.date), count(distinct c.id) from projecthistory_commitevent as c, projecthistory_path as p where c.date >= '" + str(start) + "' and c.date < '" + str(stop) + "' and p.module_id = " + str(module_id) + " and p.event_id = c.id group by DATE(c.date) order by c.date")         
    else:
        cursor.execute("select DATE(c.date), count(distinct c.id) from projecthistory_commitevent as c where c.date >= '" + str(start) + "' and c.date < '" + str(stop) + "' group by DATE(c.date) order by c.date")
    next_tuple = cursor.fetchone()

    stats = []
    while d < stop:
        day = []
        day.append(str(d))
        next = d + timedelta(1)
        if not next_tuple == None and next_tuple[0]==d: 
            day.append(log_normalize(next_tuple[1],max))
            next_tuple = cursor.fetchone()
        else:
            day.append(0.0)
        stats.append(day)
        
        d = next
    
    return stats             

def authorshortname(author_name):
    max_shortname_length = 20
    # Contains just an email address, which we will shorten
    if author_name.count(" ") == 0 and author_name.count("@") == 1:
        return author_name[:author_name.rfind("@")]
    # Contains a name and an email address
    if author_name.count(" ",0,max_shortname_length) > 0 and author_name.count("@") == 1:
        return author_name[:author_name.rfind(" ",0,max_shortname_length)]
    # Contains a space (usually for the name) which we will remove everything after
    if author_name.count(" ",0,max_shortname_length) > 0:
        return author_name[:author_name.rfind(" ",0,max_shortname_length)]
    # There name is too long, but does not fit any of the cases above
    if len(author_name) > max_shortname_length:
            return author_name[:max_shortname_length]+'...'
    # Otherwise: just use their name
    return author_name

def log_normalize(count, max_count):
   #print '%d (%d)' % (count, max_count)
   l = lambda f: math.log(f+1 or 1, math.e)
   return l(count)/l(max_count)

def topauthorsfordays():
    max_date = datetime.date(2008,1,1)
    current_date = datetime.date(2006, 1, 1)
    next_date = current_date + timedelta(1)
    author_counts = {}
    while (current_date < max_date):
        day_counts = {}
        for e in _events(current_date,next_date,NewTicketEvent):
            day_counts.setdefault(e.author.id, 0)
            day_counts[e.author.id] += 1
        for e in _events(current_date,next_date,CommitEvent):
            day_counts.setdefault(e.author.id, 0)
            day_counts[e.author.id] += 1
        for e in _events(current_date,next_date,TicketChangeEvent):
            day_counts.setdefault(e.author.id, 0)
            day_counts[e.author.id] += 1    
        sorted_day_counts = day_counts.items()
        sorted_day_counts.sort(lambda a,b: cmp(b[1], a[1]))
        if sorted_day_counts != []:
            author_counts.setdefault(sorted_day_counts[0][0], 0)
            author_counts[sorted_day_counts[0][0]] += 1    
        current_date = next_date
        next_date = current_date + timedelta(1)
    sorted_day_counts = author_counts.items()
    sorted_day_counts.sort(lambda a,b: cmp(b[1], a[1]))    
    for a in sorted_day_counts:
        print '%d\t%d' % a
    return sorted_day_counts
        
        