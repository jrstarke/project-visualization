import loadsvn,models

def svnstats(location):
    commits, authors, modules = loadsvn.get_entries_from_log(location)
    print "number of commits: " + str(len(commits))
    print "number of authors: " + str(len(authors))
    print "number of modules: " + str(len(modules)) 
    
    author_commits = {}
    for commit in commits:
        author_commits.setdefault(commit.author.name,[]).append(commit)
    items = author_commits.items()
    author_counts = []
    for item in items:
        author_counts.append((item[0],len(item[1])))
    author_counts.sort(lambda a,b: cmp(b[1],a[1]))
    print "commit distribution:"
    print author_counts                    
            

    