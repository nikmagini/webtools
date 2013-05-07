import time, calendar, datetime
import sys
from copy import copy, deepcopy

class LoggerConfig (object):
    stream = property (lambda self : self.__stream)
    detailLevel = property (lambda self : self.__detailLevel)
    filter = property (lambda self : self.__filter)
    
    def __init__ (self, stream, detailLevel, filter, owner):
        self.__stream = stream
        self.__detailLevel = detailLevel
        self.__filter = filter
        self.__owner = owner
    
    def __checkOwnerAndSet (self, what, value, owner):
        assert (owner == self.__owner)
        setattr (self, "_LoggerConfig" + what, value)
        
    def setStream (self, value, whoami):
        self.__checkOwnerAndSet ("__stream", value, whoami)
        
    def setDetailLevel (self, value, whoami):
        self.__checkOwnerAndSet ("__detailLevel", value, whoami)

    def setFilter (self, value, whoami):
        if type (value) != list:
            return
        self.__checkOwnerAndSet ("__filter", value, whoami)
    
    def ownedBy (self, owner):
        return self.__owner == owner

    def clone (self, newOwner):
        copy = deepcopy (self)
        copy.__owner = newOwner
        return copy
    
class Logger (object):
    """ Generic logger class.
    An instance of this class can usually be obtained from the context with:
    
    context.Logger ()
    
    According to the different kind of message you want to print, you can use either the
    message, warning or debug methods.
    The methods themself usually take as input a string message and an optional 
    dictionary to fill in the string following python string formatting rules.    
    If an object if passed rather than a string, it is __repr__ before printing it.
    """
    detailLevel = property (lambda self : self.config.detailLevel,
                            lambda self, value : self.__modifyConfig (LoggerConfig.setDetailLevel, value))
    
    detailFilter = property (lambda self : self.config.filter,
                             lambda self, value : self.__modifyConfig (LoggerConfig.setFilter, value))

    stream = property (lambda self : self.config.stream,
                       lambda self, value : self.__modifyConfig (LoggerConfig.setStream, value))

    config = property (lambda self : self.__config,
                       lambda self, value : self.setConfig (value))
    
    def __init__ (self, streamName, stream=sys.stderr, parent=None, standalone=False):
        self.__streamName = streamName
        if not parent and not standalone:
            parent = g_Logger
        if parent:
            assert (type (parent) == Logger)
            self.__config = parent.__config
        else:
            self.__config = LoggerConfig (stream, 10, [], self)
        
    def message (self, message, dictionary={}):
        self.log (message, dictionary, priority=0, format="[%(stream_name)s : %(date)s] message: ")
    
    def warning (self, message, dictionary={}):
        self.log (message, dictionary, priority=10, format="[%(stream_name)s : %(date)s] warning: ")
    
    def error (self, message, dictionary={}):
        self.log (message, dictionary, priority=-10, format="[%(stream_name)s : %(date)s] error: ")
    
    def debug (self, message, dictionary={}):
        self.log (message, dictionary, priority=20, format="[%(stream_name)s : %(date)s] debug: ")
    
    def trace (self, message, dictionary={}):
        self.log (message, dictionary, priority=30, format="[%(stream_name)s : %(date)s] trace: ")

    def log (self, message, dictionary={}, priority=10, format="[%(stream_name)s : %(date)s] log: "):
        dictionary["stream_name"]  = self.__streamName
        dictionary["date"] = datetime.datetime.now ()
        if (type (message) == type (str)):
            body = message % dictionary
        else:
            body = "%s" % message
        header = format % dictionary
        if self.config.detailLevel < priority:
            return 
        
        if self.config.filter and priority not in self.config.filter:
            return
            
        self.config.stream.write (header + (body))
        self.config.stream.write ("\n")
    
    def setConfig (self, config):
        self.__config = config
    
    def __cloneIfNotOwner (self):
        if not self.__config.ownedBy (self):
            self.__config = self.__config.clone (self)
        
    def __modifyConfig (self, method, value):
        self.__cloneIfNotOwner ()
        method (self.config , value, self)
                    
g_Logger = Logger ("BONSAI", standalone=True)