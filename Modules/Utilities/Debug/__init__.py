from datetime import datetime

LOG_LEVEL = 0

def log (log_text, level=0):
    if level >= LOG_LEVEL:
        tabbing = ""
        for x in range (0, level-LOG_LEVEL):
             tabbing += "   "
        print tabbing + log_text

def trace (function):
    def wrapper (*__args):
        log ("Entering: %s.%s" % (__args[0].__class__, function.__name__), 1)
        result = function (*__args)
        log ("Exiting: %s.%s" % (__args[0].__class__, function.__name__), 1)
        return result
    wrapper.__name__ = function.__name__
    return wrapper

def time_me (function):
    def wrapper (self, *__args, **__kw):
        initialTime = datetime.now ()
        result = function (self, *__args, **__kw)
        finalTime = datetime.now ()
        print "*****Function %s took %s" % (function.__name__ , finalTime - initialTime)
        return result
    wrapper.__name__ = function.__name__
    wrapper.__doc__ = function.__doc__ 
    return wrapper