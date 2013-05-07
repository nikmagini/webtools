from Cheetah.Template import Template
from os import listdir
from os.path import exists, isfile
import cherrypy
from cherrypy import expose
from Modules.Utilities.Serializers.XML import XMLSerializer
from Modules.Utilities.Debug import log
from Tools.Functors import AlwaysFalse

cherrypyDebug=False

def webmethod (func):
    def wrapperDebug (self):
        funcName = func.__name__
        variables = func (self)
        if not self.compiledTemplates.has_key (funcName):
            log ("New template instantiated", 1)
            self.compiledTemplates[funcName] = Template (self.templates[funcName], 
                                                         searchList=[variables])
        return str (self.compiledTemplates[funcName])
    def wrapper (self):
        funcName = func.__name__
        variables = func (self)
        return str (Template (self.templates[funcName], searchList=[variables]))
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    wrapperDebug.__name__ = func.__name__
    if cherrypyDebug:
        wrapperDebug.exposed = True
        return wrapperDebug
    else:
        wrapper.exposed = True
        return wrapper

def templatepage (func):
    def wrapperDebug (self, **kwds):
        funcName = func.__name__
        variables = func (self, **kwds)
        if not self.compiledTemplates.has_key (funcName):
            variables["context"] = self.context
            self.compiledTemplates[funcName] = Template (self.templates[funcName], 
                                                         searchList=[variables])
        return str (self.compiledTemplates[funcName])
    def wrapper (self, *args, **kwds):
        funcName = func.__name__
        variables = func (self, *args, **kwds)
        variables["context"] = self.context
        try:
            page = str(Template (self.templates[funcName], searchList=[variables]))
        except UnicodeDecodeError:
            page = 'Unable to parser template, funcName=%s, variables=%s' \
                % (funcName, str(variables))
        return page
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    wrapperDebug.__name__ = func.__name__
    if cherrypyDebug:
        wrapperDebug.exposed = True
        return wrapperDebug
    else:
        wrapper.exposed = True
        return wrapper

def exposeSerialized (serializer=XMLSerializer ()):
    def decorator (func):
        def wrapper (self, *args, **kwds):
            data = serializer (func (self, *args, **kwds))
            cherrypy.response.headers['Content-Length'] = str (len(data))
            cherrypy.response.headers['Content-Type'] = serializer.DATA_TYPE
            return str (data)
        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__
        wrapper.exposed = True
        return wrapper
    return decorator

def templateXML (func):
    def wrapper (self, **kwds):
        funcName = func.__name__
        variables = func (self, **kwds)
        variables["context"] = self.context
        data = str (Template (self.templates[funcName], searchList=[variables]))
        cherrypy.response.headers['Content-Length'] = str (len (data))
        cherrypy.response.headers['Content-Type'] = "text/xml"
        return str (data)
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    wrapper.exposed = True
    return wrapper

def templateJS (func):
    def wrapper (self, **kwds):
        funcName = func.__name__
        variables = func (self, **kwds)
        variables["context"] = self.context
        data = str (Template (self.templates[funcName], searchList=[variables]))
        cherrypy.response.headers['Content-Length'] = str (len (data))
        cherrypy.response.headers['Content-Type'] = "text/javascript"
        return str (data)
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    wrapper.exposed = True
    return wrapper

        


def rpccall (func):
    def wrapper (self, **kwds):
        return func (self, **kwds)
    wrapper.__doc__ = func.__doc__
    wrapper.exposed = True
    return wrapper

def xmlBooleanResponse (func):
    """If the decorated function returns True, this decorator returns "<ok/>" otherwise
       it returns "<error/>".
    """
    def wrapper (self, **kwds):
        returnValue = "<ok/>"
        result = func (self, **kwds)        
        if not result:
            returnValue = "<error/>"
        elif type (result) == tuple:
            try:
                result, extra = result
                if result:
                    returnValue = "<error reason=\"%s\"/>" % extra
                else:
                    returnValue = "<ok extra=\"%s\">" % extra
            except:
                returnValue = "<error reason=\"return value has wrong format: %s\"/>" % result
        cherrypy.response.headers['Content-Length'] = str (len (returnValue))
        cherrypy.response.headers['Content-Type'] = "text/xml"
        return returnValue
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = wrapper.__name__
    wrapper.exposed = True
    return wrapper

def require_args (*args, **kw):
    """This decorator is used to make sure that the list of keyword arguments passed to it (as strings) are
       there when calling the decorated method. If not, the __call__ method of the kw["onFail"] functor is
       called.  
    """
    def decorator (func):
        def wrapper (self, *__args, **__kw):
            for arg in args:
                if not __kw.has_key (arg):
                    if kw.has_key ("onFail"):
                        return kw["onFail"](self, *__args, **__kw)
                    else:
                        return bool ()
            print __args
            return func (self, *__args, **__kw)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator        

class Controller (object):
    """ Controller is the parent class of any Web service. Any class that exposes web methods via 
    the cherrypy "@expose" decorator or any of the similar decorators found in this module should inherit from
    this.
    As such this class does not make much sense alone but its methods are used by some implementation.
    A module containing a Controller class should always have the following directory structure.
    SomeController/
                  /js
                  /html
                  /images
                  /css
                  /Templates
    the contructor of this class will make sure that the directories js, html, images, css are visible from the web
    by pointing the browser to http://server:port/SomeController/{js, html, images, css}.
    The Templates directory will be used instead as a storage area for templated web pages (using cheetah) which 
    can be filled by method decorated with template 
    """
    def applyToTemplate (self):
        self.context.Logger ().debug ("applyToTemplate: %s" % name)
        
    def __init__(self, context, moduleFile):
        """
        The constructor of a Controller is never called direc
        passed a Contex "context" where it can lookup for services
        instanciated by the main application. Moreover it 
        """
        self.context = context
        self.moduleLocation = (moduleFile.rsplit ("/", 1)[0])
        context.Logger ().debug ("Module location %s" % self.moduleLocation)
        self.compiledTemplates = {}
        className = self.__class__.__name__
        classTemplatesDir = self.moduleLocation + "/Templates"
        
        self.templates = {}
        templateDir = "Templates/%s/" % className
        templates = []
        
        if exists (templateDir):
            templates += listdir (templateDir)
            
        if exists (classTemplatesDir):
            templates += listdir (classTemplatesDir)
                    
        for template in templates:
            name = template.split (".")[0]
            filename = classTemplatesDir + "/" + template
            if not isfile (filename):
                filename = templateDir + template
            
            if isfile (filename):
                self.namespace = {}
                f = file (filename)
                self.templates[name] = f.read ()
        from os import getcwd
        from os.path import join
        abspath = join ("/", getcwd (), self.moduleLocation)
        self.config = {}
        for relPath in ["/css", "/js", "/jstest", "/images", "/html", "/download"]:
            if exists (abspath + relPath):
                self.config[relPath] = {"tools.staticdir.on": True,
                                        "tools.staticdir.dir": abspath + relPath}

    @templatepage
    def apidoc (self):
        """Returns the documentation page."""
        methods=[]
        for key in dir (self):
            method = getattr (self, key)
            try:
                isExposed = getattr (method, "exposed")
                methods.append ({"name": key, "documentation": method.__doc__})
            except:
                pass
        return {'module': {"name": self.__class__.__name__},
                'methods': methods}

    def templatePage (self, templateName, variables):
        variables["context"] = self.context
        return str (Template (self.templates[templateName], searchList=[variables]))

    def readyToRun (self):
        """ This method (or its implementation in a child class) is called by the main application 
        right before the server starts listening on some port.
        """
        pass
        
#   def initFileMethods (self, directory):
#       className = self.__class__.__name__
#       fileDir = "%s/%s" % (className, directory)
#       files = listdir (fileDir)
#       files.remove ("CVS")
#       for f in files:
#           fileName = fileDir + f
#           def wrapper (self):
#               return file (open (fileName)).read ()
#           wrapper.exposed = True
#           self.__dict__[fileName] = wrapper
