import re,os
from datetime import datetime,timedelta
from time import strptime
import models
    
def parse_date(date_str):
    date_str = date_str[:19]
    return datetime(*strptime(date_str, '%Y-%m-%d %H:%M:%S')[0:6])

# returns the parts of a log entry line in the format:
# r3862 | jon.smith | ...
def info_line_parts(line):
    revision, author, date, stat = line.split(' | ')
        
    return int(revision[1:]), author, parse_date(date), \
        int(stat.split(' ')[0])

# returns the first element of the given list and the rest
# of the list
def pop(lines):
    if lines:
        return lines[0].strip(), lines[1:]
    return None, []
    
    
# returns a LogEntry based on lines from the svn log command
def parse_entry(lines):
    entry = models.Commit()
    
    # details
    line, lines = pop(lines)
    try:
        entry.id, author_name, entry.date, entry.lines = \
            info_line_parts(line)
        entry.author = models.Author.from_string(author_name)
        
    except ValueError:
        print line
        print lines
        print 'error'
        return None
    
    # paths
    line, lines = pop(lines)
    if line == 'Changed paths:':
        while True:
            line, lines = pop(lines)
            if line == None or line == '': 
                break
            line = line.strip()
            
            match = re.match(r'^(.) ([^(]+)(?: \(from (.+):(\d+)\))?$', line)
            groups = match.groups()
            
            entry.add_path(groups[0], 
                groups[1],
                groups[2],
                groups[3],
                models.Module.from_svn_path(groups[1]))
    
    # message lines
    entry.message = "\n".join(lines)
    
    return entry

# splits the string returned by "svn log" into specific entries
def split_log_string(log_string):
    return [s.strip().split("\n") for s in 
        re.split(r'-{72}', log_string) if s.strip() != '']

# returns a list of LogEntry objects
def get_entries(log_string):
    entries = [parse_entry(lines) for lines in 
        split_log_string(log_string)]
    return filter(None, entries)

def get_entries_from_file(file_name):
    f = open(file_name)
    entries = get_entries(f.read())
    f.close()
    return entries

def get_entries_from_log(location):
    models.Collection.Handle().clear()
    log = get_svn_log(location)
    entries = get_entries(log)
    authors = models.Collection.Handle().authors
    modules = models.Collection.Handle().modules
    return entries, authors, modules

def get_svn_log(location):
    #output = os.popen("svn log " + location + " -v")
    currentdate = datetime.today().date()
    back_180 = currentdate - timedelta(30)
    output = os.popen("svn log " + location + " -v -r {" + str(currentdate)+ "}:{" + str(back_180) + "}")
    return output.read()   
