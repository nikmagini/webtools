from os.path import exists, join, isdir
from os import getenv, listdir
from os import environ
from pickle import load
import sys
from Framework.Logger import Logger

import traceback

g_pluginRegistry = {}

g_pluginLogger = Logger ("Plugin Engine")

class PluginContainer (object):
    def __init__ (self, implementation, options={}, name=""):
        self.implementation = implementation
        self.options = options
        self.name = name
    
    def createInstance (self, *args, **kwds):
        return self.implementation (*args, **kwds)

def plugin (name, options={}):
    def decorator (function):
        def wrapper (self, *__args, **__kw):
            global g_pluginRegistry
            g_pluginLogger.debug ("Declaring plugin %s with implementation %s" % (name, function))
            g_pluginRegistry [name] = PluginContainer (function, options, name=name)
            return function (*__args, **__kw)
        return wrapper
    return decorator

class DeclarePlugin (object):
    def __init__ (self, name, implementation, options={}):
        global g_pluginRegistry
        g_pluginLogger.debug ("Declaring plugin %s with implementation %s" % (name, implementation))
        g_pluginRegistry[name] = PluginContainer (implementation, options, name)

class PluginManager (object):
    def __init__ (self, cfgFileName):
        self.bonsaiRoot = getenv ("BONSAI_ROOT", "./")
        self.restoreCache ()
        self.loadComponents ()
        
    def restoreCache (self):
        self.cachePath = join (self.bonsaiRoot, ".cache")
        if exists (self.cachePath):
            self.cache = load (self.cachePath)
    
    def loadComponents (self):
        self.pluginPaths = ["Modules", "Applications", "Controllers"]
        if getenv ("BONSAI_PLUGIN_PATH"):
            self.pluginPaths.append (getenv ("BONSAI_PLUGINS_PATH").split (":"))
        
        for path in self.pluginPaths:
            for pythonPath in sys.path:
                newPythonPath = join (pythonPath, path)
                sys.path.insert (0, newPythonPath)                
                if exists (newPythonPath):
                    fileList = listdir (newPythonPath)
                    for pythonFile in fileList:
                        if pythonFile[0] == ".":
                            pass
                        elif pythonFile in ("__init__.py", "__init__.pyc", "CVS"):
                            pass
                        elif isdir (join (newPythonPath, pythonFile)) or pythonFile.endswith (".py"):
                            try:
                                moduleName = pythonFile.replace (".py", "")
                                g_pluginLogger.debug ("Attempting to load %s" % moduleName)
                                mod = __import__ (moduleName)
                                g_pluginLogger.debug ("Done loading %s" % mod)
                            except ImportError, (e):
                                message = "Unable to import %s because: %s\n" % (pythonFile, e)
                                exceptionStrings = traceback.format_exception (sys.exc_type, sys.exc_value, sys.exc_traceback)
                                g_pluginLogger.warning ("Error in parsing %s for DeclarePlugin statements. File will not be consider by the plugin loader." % pythonFile)
                                g_pluginLogger.debug (message + "\t".join (exceptionStrings))
                        else:
                            pass
                sys.path.pop (0) 
        g_pluginLogger.debug (g_pluginRegistry)
        
    def plugins (self, nameFilter=""):
        pluginList = []
        for name, plugin in g_pluginRegistry.items ():
            if name.startswith (nameFilter):
                pluginList.append (plugin)
        return pluginList
