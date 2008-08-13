from datetime import date

class Collection:
    __single = None
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
    directory = ''
    
    @classmethod
    def from_path(cls,full_path):
        module = Module()
        module.directory = full_path[:full_path.rfind('/')]
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
    action = ''
    dest_file = ''
    src_file = ''
    src_revision = ''
    module = ''
    
    def __repr__(self):
        return '(action=' + repr(self.action) + ', dest_file=' + repr(self.dest_file) + ', src_file=' + repr(self.src_file) + ', src_revision=' + repr(self.src_revision) + ', module=' + repr(self.module) + ')'
    
class Commit:
    id = 0
    author = Author
    message = ''
    paths = []
    lines = 0
    
    def __init__(self):
        self.paths = []
    
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