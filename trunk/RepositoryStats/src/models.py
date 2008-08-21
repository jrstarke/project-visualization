from datetime import date

class Collection:
    __single = None
    
    def __init__(self):
        authors = []
        modules = []
    
    @classmethod
    def Handle (cls):
        if Collection.__single == None:
            Collection.__single = Collection()
        return Collection.__single    
    
    def clear(self):
        self.authors = []
        self.modules = []

class Author:
    
    def __init__(self):
        name = ''
    
    @classmethod
    def from_string(self,string):
        string = string.replace('&lt;','').replace('&gt;','').strip()
        author = Author()
        author.name = string
        author_list = Collection.Handle().authors
        if author in author_list:
            author = author_list[author_list.index(author)]
        else:
            author_list.append(author)
        return author
    
    def __repr__(self):
        return repr(self.name)
    def __eq__(self, other):
        if isinstance(other, Author):
            return self.name == other.name
        return NotImplemented
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

class Module:
    
    def __init__(self):
        directory = ''
    
    @classmethod
    def from_path(cls,full_path):
        module = Module()
        paths = full_path.split('/')
        if ('trunk' in paths):
            full_path = '/' + '/'.join(paths[paths.index('trunk')+1:])
        elif ('branches' in paths):
            full_path = '/' + '/'.join(paths[paths.index('branches')+2:])    
        module.directory = full_path[:full_path.rfind('/')+1]
        module_list = Collection.Handle().modules
        if module in module_list:
            module = module_list[module_list.index(module)]
        else:
            module_list.append(module)
        return module

    @classmethod
    def from_svn_path(cls,full_path):
        module = Module()
        paths = full_path.split('/')
        if ('trunk' in paths):
            full_path = '/' + '/'.join(paths[paths.index('trunk')+1:])
        elif ('branches' in paths):
            full_path = '/' + '/'.join(paths[paths.index('branches')+2:])    
        module.directory = full_path[:full_path.rfind('/')+1]
        module_list = Collection.Handle().modules
        if module in module_list:
            module = module_list[module_list.index(module)]
        else:
            module_list.append(module)
        return module


    def __repr__(self):
        return repr(self.directory)
    def __eq__(self, other):
        if isinstance(other, Module):
            return self.directory == other.directory
        return NotImplemented
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
    
class Path:
    
    def __init__(self):
        action = ''
        dest_file = ''
        src_file = ''
        src_revision = ''
        module = ''
        
    def __repr__(self):
        return '(action=' + repr(self.action) + ', dest_file=' + repr(self.dest_file) + ', src_file=' + repr(self.src_file) + ', src_revision=' + repr(self.src_revision) + ', module=' + repr(self.module) + ')'
    
class Commit:

    def __init__(self):
        self.paths = []
        self.id = 0
	    self.author = Author
	    self.message = ''
	    self.paths = []
	    self.lines = 0    
    
    def add_path(self,action,dest_file,src_file,src_revision,module):
        path = Path()
        path.action = action
        path.dest_file = dest_file
        path.src_file = src_file
        path.src_revision = src_revision
        path.module = module
        self.paths.append(path)
        
    def modules(self):
        modules = []
        for path in self.paths:
            if path.module not in modules:
                modules.append(path.module)
        return modules
        
    def __eq__(self, other):
        if isinstance(other, Commit):
            return self.id == other.id
        return NotImplemented
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
   
    def __repr__(self):
        return '(id=' + repr(self.id) + ', author=' + repr(self.author) + ', message=' + repr(self.message) + ', lines=' + repr(self.lines) + ', paths=' + repr(self.paths) + ')'             