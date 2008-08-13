import loadsvn,models

def svnstats(location):
    commits, authors, modules = loadsvn.get_entries_from_log(location)
    print "number of commits: " + str(len(commits))
    print "number of authors: " + str(len(authors))
    print "number of modules: " + str(len(modules)) 
    
    # Compute the Distribution of commits by Author
    author_commits = {}
    module_commits = {}
    for commit in commits:
        author_commits.setdefault(commit.author.name,[]).append(commit)
        modules = []
        for path in commit.paths:
            if not path.module in modules:
                modules.append(path.module)
        for module in modules:
            module_commits.setdefault(module.directory,{}).setdefault(commit.author.name,0)        
            module_commits[module.directory][commit.author.name] = module_commits[module.directory][commit.author.name] + 1
            module_commits.setdefault(module.directory,{}).setdefault('total',0)
            module_commits[module.directory]['total'] = module_commits[module.directory]['total']+1
                
    items = author_commits.items()
    author_counts = []
    for item in items:
        author_counts.append((item[0],len(item[1])))
    # Sort the Distribution by the number of commits
    author_counts.sort(lambda a,b: cmp(b[1],a[1]))
    print
    print "commit distribution:"
    print author_counts          
    
    # Compute the number of commits to a module by a specific author
    print
    
    output = "module distribution\n\n"
    for module,authors in module_commits.items():
        output += module + "\n"
        for author,value in authors.items():
            output += author + ": " + str(value) + " "
        output += "\n\n"
    print output     
    
    #print module_commits   
            
    
        
            

    