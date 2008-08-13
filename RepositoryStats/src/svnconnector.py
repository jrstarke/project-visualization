import os

def svnlogxml(location):
    fi,fo,fe = os.popen3("svn log " + location + " -v")
    return fo
