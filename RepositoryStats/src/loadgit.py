import re,os
from datetime import datetime,timedelta
from time import strptime, strftime
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
    entry.author = models.Author.from_string(line)
    line, lines = pop(lines)
    entry.date = parse_date(line)
    line, lines = pop(lines)
    entry.message = line
    
    # paths
    line, lines = pop(lines)
    if line == 'Paths':
        while True:
            line, lines = pop(lines)
            if line == None or line == '':
                break
            elif line[0] != ':': 
                break
            
            entry.add_path(line[37], 
                line[40:],
                None,
                None,
                models.Module.from_svn_path(line[40:]))
            
    if line == None or line == '':
        None
    else :
        pattern = re.compile(r'(\d*)\D*(\d*)\D*(\d*)$', re.VERBOSE)
        groups = pattern.search(line).groups()
        entry.lines = int(groups[0]) + int(groups[1])
        #print groups
    
    # message lines
    #entry.message = "\n".join(lines)
    
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
    log = get_git_log(location)
    entries = get_entries(log)
    authors = models.Collection.Handle().authors
    modules = models.Collection.Handle().modules
    return entries, authors, modules

def get_git_log(location):
    currentdate = datetime.today().date()
    back_180 = currentdate - timedelta(30)
    date = back_180.strftime("%b %d %Y")
    child,debug =  os.popen4("git clone " + location)
    if len(debug.readlines()) is 0:
        print "No repository"
    name = (location[location.rfind("/")+1:])
    name = name[:name.rfind(".")]
    debug = os.chdir(name)
    child,output = os.popen4("git-log --pretty=format:------------------------------------------------------------------------%n%an%n%ci%n%s%nPaths --shortstat --raw --after=\"" + date + "\"")
    debug = os.chdir("..")
    return output.read()   
