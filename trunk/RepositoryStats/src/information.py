import loadsvn,models

def svnstats(location):
    commits, authors, modules = loadsvn.get_entries_from_log(location)
    print "number of commits: " + str(len(commits))
    print "number of authors: " + str(len(authors))
    print "number of modules: " + str(len(modules)) 
    
    author_commits = {}
    for commit in commits:
        author_commits[commit.author] = author_commits.setdefault(commit.author,[]).append(commit)
    print author_commits    