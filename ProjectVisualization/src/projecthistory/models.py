import os, re
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.db import models

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
    
    # returns a list of components affected by this event
    def modules(self):
        return [p.module for p in self.path_set.all()]

    class Meta:
        ordering = ['date']

class NewTicketEvent(models.Model):
    author = models.ForeignKey(Author) # initial owner
    date = models.DateTimeField()
    ticket = models.ForeignKey(Ticket, unique=True)

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

def events(start, stop):
    all_events = _events(start,stop, NewTicketEvent) + \
        _events(start,stop, CommitEvent) + \
        _events(start, stop, TicketChangeEvent)
    # should realy be merging these ...
    all_events.sort(lambda a,b: cmp(a.date, b.date))
    return all_events
    
def _events(start, stop, model):
    return list(model.objects.filter(date__range=(start, stop)))
