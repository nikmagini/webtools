from ConfigParser import ConfigParser
from Framework import Controller
from os.path import exists
from os import getenv

def upper (s):
    return s.upper ().replace ("-", "_")

def getRoot (s):
    return getenv (upper (s) + "_ROOT")
    
class StaticController (Controller):
    def __init__ (self, context, controllerName, configPath=""):
        Controller.__init__ (self, context, __file__)
        configParser = ConfigParser ()
        configFilename = configPath
        if (not exists (configPath)) and exists (getenv ("HOME") +"/" + controllerName + "/etc/cherrypy.conf"):
            configFilename = getenv ("HOME") +"/" + controllerName + "/etc/cherrypy.conf"
        elif (not exists (configPath)) and getRoot (controllerName) and exists (getRoot (controllerName) + "/etc/cherrypy.conf"):
            configFilename = getRoot (controllerName) + "/etc/cherrypy.conf"
        elif exists (configPath + "/etc/cherrypy.conf"):
            configFilename = configPath + "/etc/cherrypy.conf"
        elif exists (configPath):
            configFilename = configPath
        else:
            raise "File not found %s" % configFilename

        print "****************" + configFilename
        
        try:
            configParser.read (configFilename)
        except:
            print "Cannot read configFilename."
        self.config = configParser._sections
        print self.config