#!/usr/bin/env python
from Framework import BonsaiServer
from Framework import Context
from Framework.Logger import Logger
from Framework.Logger import g_Logger
from optparse import OptionParser
from Framework import CmdLineArgs
import sys
import os
import getpass
from os.path import abspath
import errno

class Cfg:
    def __init__ (self):
        # TODO: make it a property.
        self.installRoot = __file__.rsplit ("/", 1)[0]

class CommandFactory (object):
    def __init__ (self, context, opts, args):
        self.context = context
        self.registry = {"start": StartCommand,
                         "status": StatusCommand,
                         "stop": StopCommand}
        self.opts, self.args = opts, args
    
    def createByName (self, name):
        try:
            obj = self.registry[name] ()
        except KeyError:
            return None
        obj.context = self.context
        obj.opts = self.opts
        obj.args = self.args
        return obj

class Command (object):
    def __init__ (self):
        self.context = None
        self.opts = None
        self.args = None

    def finish (self):
        pass

def checkIfPidRunning (pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError, err:
        return err.errno == errno.EPERM

def getPidFromFile (filename):
    try:
        return int (open (filename).read ().strip ())
    except ValueError:
        print "Invalid lockfile format for %s." % filename
        print "Cannot detect status."
        sys.exit (2)

class StatusCommand (Command):
    def run (self):
        filename = abspath (self.opts.pidFile)
        try:
            pid = getPidFromFile (filename)
            if checkIfPidRunning (pid):
                print "cmsWeb is running as pid %s" % pid
                sys.exit (0)
            print "cmsWeb not running."
        except IOError:
            print "File %s does not exists." % self.opts.pidFile
            print "Cannot detect status."
            sys.exit (2)

class StopCommand (Command):
    def run (self):
        filename = abspath (self.opts.pidFile)
        username = getpass.getuser ()
        
        try:
            pid = getPidFromFile (filename)
            if self.opts.forceKill == True:
                print "Sending SIGKILL to pid %s" % pid
                os.kill (pid, 9)
                sys.exit (0)
            print "Sending SIGTERM to pid %s" % pid
            os.kill (pid, 15)
        except OSError, err:
            if err.errno == errno.EPERM:
                print "Pid %s is not owned by user %s. Cannot stop it." % (pid, username)
                sys.exit (2)
            else:
                print "Pid %s does not exists. Please remove the lock file %s." % (pid, filename) 
        except IOError:
            print "File %s does not exists." % self.opts.pidFile
            print "Cannot detect status."
            sys.exit (2)
        

class StartCommand (Command):
    def run (self):
        app = BonsaiServer (self.context)
        opts, args = self.context.OptionParser ().parse_args ()
        filename = abspath (self.opts.pidFile)
        try:
            pid = getPidFromFile (filename)
            if checkIfPidRunning (pid):
                print "A process %s is alredy running using lock file %s. Nothing is done." % (pid, filename)
                sys.exit (0)
            else:
                print "Process %s died unexpectedly. Removing lockfile %s." % (pid, filename)
                os.unlink (filename)
        except IOError:
            # TODO: this should be a warning.
            g_Logger.trace ("File %s does not exists. Will be created." % filename)
        
        open (filename, 'w').write (str (os.getpid ()))
        self.context.addService (CmdLineArgs (self.context.OptionParser ()))
        self.context.addService (Cfg ())
        if opts.profile:
            import pstats
            try:
                import cProfile as profile
            except ImportError: 
                import profile
            profile.run ('app.start ()', 'bonsaiProfiler')

            p = pstats.Stats ('bonsaiProfiler')
            p.strip_dirs().sort_stats (-1).print_stats()        
        else:
            app.start ()
    
    def finish (self):
        filename = abspath (self.opts.pidFile)
        try:
            os.unlink (filename)
        except IOError:
            print "Unable to remove lock file %s" % filename

def getValidOptions (iargs):
    validArguments = ["start", 
                      "stop", 
                      "restart",
                      "status"]
    validOptions = ["--cfg", "--force-kill", "--pid-file", 
                    "--log-file", "--log-level"]

    args = []
    for arg in iargs:
        for item in arg.split('='):
            args.append(item)
    result = []
    for i in range (0, len (iargs)):
        arg = sys.argv[i]
        if arg in validArguments:
            result.append (args[i])
    
    for i in range (0, len (args)):
        option = args[i]
        if option in validOptions:
            result.append (option)
            result.append (args[i+1])
    return result

class CmsWebApplication (object):
    def __init__ (self):
        self.context = Context ()
        self.context.addService (OptionParser ())
        self.parser = self.context.OptionParser ()
        self.__addOptions ()
        
    def __addOptions (self):
        self.parser.add_option ("--profile",
                           help="start server in profiler mode",
                           default=False,
                           action="store_true",
                           dest="profile")

        self.parser.add_option ("--pid-file",
                           help="File in which it is specified the pid of wanted instance",
                           default="pid.txt",
                           dest="pidFile",
                           metavar="FILE")

        self.parser.add_option ("--force-kill",
                           help="Uses SIGKILL rather than SIGTERM",
                           default=False,
                           action="store_true",
                           dest="forceKill",
                           metavar="FILE")
                           
        def openFilename (option, opt_str, value, parser, *args, **kwargs):
            try:
                f=open (value, 'a')
            except IOError:
                print "WARNING: Unable to open log file %s. Using stderr." % value
                f=sys.stderr
            setattr (parser.values, option.dest, f)
        
        self.parser.add_option ("--log-file",
                           help="FILE to which redirect log messages",
                           dest="logFile",
                           default=sys.stderr,
                           action="callback",
                           callback=openFilename,
                           metavar="FILENAME",
                           type="str",
                           nargs=1)
                           
        self.parser.add_option ("--log-level",
                            help="detail LEVEL for the main log",
                            dest="logLevel",
                            default=10,
                            metavar="LEVEL",
                            type="int")
    
    def run (self):
        if "--help" in sys.argv:
            g_Logger.detailLevel = -100
        validOptions = getValidOptions (sys.argv)

        opts, args = self.parser.parse_args (args=validOptions)

        g_Logger.stream = opts.logFile
        if "--help" not in sys.argv:
            g_Logger.detailLevel = opts.logLevel
        
        if not len (args):
            args = ["start"]
        
        factory = CommandFactory (self.context, opts, args)
        startCommand = factory.createByName (args[0])
        if not startCommand:
            "Command %s not known." % args[0]
            sys.exit (1)
        startCommand.run ()
        startCommand.finish ()

if __name__ == '__main__':
    app = CmsWebApplication ()
    app.run ()
