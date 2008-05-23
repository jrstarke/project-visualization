import os, re, datetime
from projectstats import models

def sort(items):
    def _cmp(a,b):
        return cmp(b[1], a[1])
    items.sort(_cmp)
    return items

def date_groups():
    date = datetime.date(2006, 12, 31)
    groups = []
    for x in range(4):
        group = []
        for y in range(4):
            date = date + datetime.timedelta(7)
            next_date = date + datetime.timedelta(7)
            group.append((date,next_date))
        groups.append(group)
    return groups
    
def _most_modified_files(groups, n=5):
    files = {}
    for group in groups:
        for date_range in group:
            entries = models.LogEntry.objects.filter(date__range=date_range)
            for e in entries:
                for path in e.path_set.all():
                    if path.dest_file.endswith(".py"):
                        incr(files, path.dest_file)                    
    files = sort(files.items())
    return dict(files[:n])
    
def incr(values, key, add=True):
    if not values.has_key(key):
        if add:
            values[key] = 0
        else:
            return
    values[key] += 1
   
def most_active_authors_string(author_counts, n=4):
    return ", ".join(["%s %d" % (models.Author.objects.get(pk=i).name,c) \
        for i,c in sort(author_counts.items())[:n]])

def tracstats(groups):
    most_modified_files = _most_modified_files(groups, 15)
    total_active_fixers = {}
    for group in groups:
        active_tickets = {}
        active_fixers = {}
        
        total_opened = 0
        total_closed = 0
        
        print '-------------------------------------------------------'
        for date_range in group:
            #print date_range
            opened = models.Ticket.objects.filter(open_date__range=date_range).count()
            closed = models.Change.objects.filter(changed_field='status', to_value='closed', date__range=date_range).count()

            total_opened += opened
            total_closed += closed

            print "%d opened, %d closed" % (opened*2, closed*2) # *2 is to scale diagram
            for change in models.Change.objects.filter(date__range=date_range):
                incr(active_tickets, change.ticket.id)
                
                if change.changed_field == 'resolution' and change.to_value == 'fixed':
                    incr(active_fixers, change.ticket.owner.id)
                    incr(total_active_fixers, change.ticket.owner.id)
                    
        print most_active_authors_string(active_fixers)
        print ", ".join(["%s (%d)" % (models.Ticket.objects.get(pk=i), c) \
            for i,c in sort(active_tickets.items())[:4]])
        print "%d new issues opened, %d issues closed" % (total_opened,total_closed)
        
    print '-------------------------------------------------------'
    print '---- CURRENTLY ----------------------------------------'
    print '-------------------------------------------------------'
    
    print most_active_authors_string(total_active_fixers, 10)
    
    owners = {}
    
    opened = models.Ticket.objects.exclude(status='closed')
    currently_open = opened.count()
    currently_unreviewed = opened.filter(stage='Unreviewed').count()
    
    for ticket in opened:
        incr(owners, ticket.owner.id)
    print "%d opened, %d unreviewed" % (currently_open, currently_unreviewed)
    print "%d opened, %d unreviewed" % (currently_open/2, currently_unreviewed/2) #/2 is to scale diagram
    print most_active_authors_string(owners)
    
    nobody = models.author('nobody')
    oldest = models.Ticket.objects.exclude(owner=nobody).exclude(status='closed').exclude(stage='Accepted').order_by('open_date')[:10]
    
    print "oldest issues", 
    print ", ".join(["%d %s" % (t.id, t.owner.name) for t in oldest])
    
    #for ticket in oldest:
    #    print "%s %s %s %s" % (ticket.owner.name, ticket, ticket.stage, ticket.open_date)
    

def svnstats(groups):
    most_modified_files = _most_modified_files(groups, 6)
    author_mods_by_file = {}
    
    total_revs = 0
    total_a = 0
    total_m = 0
    total_d = 0
    
    issues = {}
    total_authors = {}
    
    for group in groups:
        authors = {}
        
        count_matching_isses = 0
        group_total_a = 0
        group_total_m = 0
        group_total_d = 0
        group_total_revs = 0
            
        print '-------------------------------------------------------'
        for date_range in group:
            #print date_range
            files = dict([(f,0) for f in most_modified_files.keys()])
            entries = models.LogEntry.objects.filter(date__range=date_range)
    
            group_total_revs += len(entries)
            total_revs += len(entries)
            total_matching_issues = 0
            
            for e in entries:
                
                # check if this goes with a trac issue
                match = re.match(r'.*#(\d{2,4}).*', e.message)
                if match:
                    incr(issues, match.group(1))
                    total_matching_issues += 1
                
                for path in e.path_set.all():
                    if path.action == 'A': group_total_a += 1
                    if path.action == 'M': group_total_m += 1
                    if path.action == 'D': group_total_d += 1
                    
                    incr(files, path.dest_file, False)
                    if not author_mods_by_file.has_key(path.dest_file):
                        author_mods_by_file[path.dest_file] = {}
                    incr(author_mods_by_file[path.dest_file], e.author.id)
                    
                incr(authors, e.author.id)
                incr(total_authors, e.author.id)
                
            #print "     %d revs, M:%d A:%d D:%d" % (len(entries)*3, group_total_m*2, group_total_a*2, group_total_d*2)
            print "%d (%d)" % (len(entries),total_matching_issues)
            count_matching_isses += total_matching_issues
            
            for f,count in files.items():
                parts = f.split('/')
                if count >= 8:
                    color = '25%'
                elif count >= 6:
                    color = '50%'
                elif count >= 2:
                    color = '50%'
                elif count >= 1:
                    color = '75%'
                else:
                    color = '100%'
                
                print "    .../%s/%s %d %s" % (parts[-2],parts[-1], count, color)
            
        total_a += group_total_a
        total_m += group_total_m
        total_d += group_total_d
        
        print "%d commits (%d issues) %d modified %d added %d deleted" % (group_total_revs, count_matching_isses, group_total_m, group_total_a, group_total_d)
        print most_active_authors_string(authors)
        
    print '-----------------------------------------------------------'
    print '--- OVER ALL GROUPS ---------------------------------------'
    print '-----------------------------------------------------------'
    
    print "%d revs, A:%d M:%d D:%d" % (total_revs, total_a, total_m, total_d)
    print "%d revs, A:%d M:%d D:%d" % (total_revs, total_a/2, total_m/2, total_d/2)

    print sort(issues.items())[:10]
    print most_active_authors_string(total_authors, 10)
    
    return
    
    for f, fcount in most_modified_files.items():
        print f, fcount
        print "    ", most_active_authors_string(authors)
        mods_by_file = sort(author_mods_by_file[f].items())[:3]
        for a, count in mods_by_file:
            print "    ", models.Author.objects.get(pk=a).name, count


def summarize_component_stats(opened_dict, closed_dict, mods_dict, authors_dict, files_dict={}):
    components = sort(opened_dict.items())[:8]
    for c, count in components:
        print models.Component.objects.get(pk=c).name
        print "%d opened %d closed %d files modified" % (count, closed_dict.get(c,0), mods_dict.get(c,0))
        print most_active_authors_string(authors_dict[c])
        
        file_list = sort(files_dict.get(c,{}).items())[:8]
        s = ", ".join(["%s %d" % (f.split('/')[-1], c) for f,c in file_list])
        print s
        print
        #for f,c in file_list:
        #    print "    ", f, c


def componentstats(groups):
    max_opened = 60.0
    max_closed = 60.0
    max_mods = 150.0
    
    total_opened_by_component = {}
    total_closed_by_component = {}
    total_mods_by_component = {}
    blank_authors = dict([(a.id,0) for a in models.Author.objects.all()])
    total_authors_by_component = dict([(c.id,dict(blank_authors)) for c in models.Component.objects.all()])
    total_files_by_component = {}
    
    for group in groups:
        print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        opened_by_component = {}
        closed_by_component = {}
        mods_by_component = {}
        authors_by_component = dict([(c.id,dict(blank_authors)) for c in models.Component.objects.all()])
        files_by_component = {}
        
        print "%s to %s" % (group[0][0], group[-1][-1])
        for date_range in group:
            
            opened = models.Ticket.objects.filter(open_date__range=date_range)
            closed = models.Change.objects.filter(changed_field='status', to_value='closed', date__range=date_range)
            
            for ticket in opened:
                incr(opened_by_component, ticket.component.id)
                incr(total_opened_by_component, ticket.component.id)
                #incr(authors_by_component[ticket.component.id], ticket.owner.id)
                #incr(total_authors_by_component[ticket.component.id], ticket.owner.id)
                
            for change in closed:
                incr(closed_by_component, change.ticket.component.id)
                incr(total_closed_by_component, change.ticket.component.id)
            
            for e in models.LogEntry.objects.filter(date__range=date_range):
                for p in e.path_set.all():
                    if not total_files_by_component.has_key(p.component.id):
                        total_files_by_component[p.component.id] = {}
                    incr(total_files_by_component[p.component.id], p.dest_file)

                    if not files_by_component.has_key(p.component.id):
                        files_by_component[p.component.id] = {}
                    incr(files_by_component[p.component.id], p.dest_file)

                    incr(mods_by_component, p.component.id)
                    incr(total_mods_by_component, p.component.id)
                    incr(authors_by_component[p.component.id], e.author.id)
                    incr(total_authors_by_component[p.component.id], e.author.id)
        
        #components = sort(opened_by_component.items())[:5]
        #for c, count in components:
        #    print models.Component.objects.get(pk=c).name, count
            
        #summarize_component_stats(opened_by_component, closed_by_component,
        #    mods_by_component, authors_by_component)
        
        components = sort(opened_by_component.items())[:8]
        for c, count in components:
            if models.Component.objects.get(pk=c).name in ['django.newforms', 'django.db', 'django.contrib.admin']:            
                s = "%s\n%d O, %d C, %d M" % \
                    (models.Component.objects.get(pk=c).name, count, 
                    closed_by_component.get(c,0), mods_by_component.get(c,0))
                print s
                print most_active_authors_string(authors_by_component[c],4)
                file_list = sort(files_by_component.get(c,{}).items())[:3]
                for f,c in file_list:
                    print "%s %d" % (f.split('/')[-1], c)
                print
        
        #return
           
        #for c,count in opened_by_component.items():
        #    if count > max_opened:
        #        max_opened = count
                
        #for c,count in closed_by_component.items():
        #    if count > max_closed:
        #        max_closed = count

        #for c,count in mods_by_component.items():
        #    if count > max_mods:
        #        max_mods = count

    print "\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    print "++++++ OVER ALL GROUPS ++++++++++++++++++++++++++++++++++"
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    print "\nopen, closed, mods"

    summarize_component_stats(total_opened_by_component, total_closed_by_component,
            total_mods_by_component, total_authors_by_component, total_files_by_component)
    
    #print max_opened
    #print max_closed
    #print max_mods
    
#svnstats(date_groups())
#tracstats(date_groups())
componentstats(date_groups())