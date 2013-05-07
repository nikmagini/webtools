import cherrypy
import os
import socket
from Framework.PluginManager import PluginManager
from Framework.Context import Context
from Framework.Logger import Logger
from Modules.Utilities.Debug import log
from Cheetah.Template import Template
from Framework import templateErrorHandler
import traceback
import sys

def getExcMessage():
    msg = ""
    counter=0
    for m in  traceback.format_exc().split("\n"):
        if  m.find(" raise ")!=-1:
            counter = 1
            continue
        if  counter:
            msg += m
    return msg

class HttpsOnlyFilter (object):
    def __init__ (self, redirect):
        self.redirect = redirect
    def __call__ (self):
        if (cherrypy.request.query_string) and (not "https" in cherrypy.request.query_string):
            raise cherrypy.HTTPRedirect (self.redirect)

class BonsaiServer (object):
    def __init__ (self, context):
        self.context = context
        self.__addCommandLineOptions ()
        self.context.addService (PluginManager ("bonsai.cfg"))
        self.controllers = []
        self.services = []
        self.logger = Logger ("Server")
        self.context.addService (self.logger)
        
        self.__loadServices ()
        self.__loadControllers ()
        self.mountControllers ()
    
    def __addCommandLineOptions (self):
        parser = self.context.OptionParser ()
        parser.add_option ("-s", "--secure", 
                           help="redirects to URL if the connection is not secure", 
                           dest="secureRedirect",
                           metavar="URL",
                           default="")
        
        parser.add_option ("--ssl", 
                           help="start bonsai server in SSL mode, host CA/KEY can be setup via BONSAI_CA/BONSAI_KEY environment", 
                           dest="ssl",
                           action="store_true",
                           default=False)

        parser.add_option ("-p", "--port",
                           help="server listening on port PORT",
                           dest="port",
                           metavar="PORT",
                           default="8030")
        
        parser.add_option ("-e", "--environment",
                           help="server environment (production|development)",
                           dest="environment",
                           metavar="ENV",
                           default="production")
        
        parser.add_option ("--default-page",
                           dest="defaultPage",
                           metavar="URL",
                           default="/Studio/login")
        def stripTrailingSlash (option, opt_str, value, parser, *args, **kwargs):
            setattr(parser.values, option.dest, value.rstrip ("/"))
        
        parser.add_option ("--base-url",
                           help="Base URL for the server (for usage behind a proxy).",
                           default="http://localhost:8030",
                           dest="baseUrl",
                           action="callback",
                           callback=stripTrailingSlash,
                           type="str",
                           nargs=1)
    
    def __loadServices (self):
        for plugin in self.context.PluginManager ().plugins ("/Services"):
            # Services are loaded before /Controllers to provide them with
            # general utilities.
            serviceName = plugin.implementation.__name__
            self.logger.debug ("Loading service: %s" % serviceName)
            try:
                service = plugin.createInstance (self.context)
                self.services.append (service)
            except Exception, e:
                message = "An error was found while loading the service: %s.\n" % serviceName
                exceptionStrings = traceback.format_exception (sys.exc_type, sys.exc_value, sys.exc_traceback)
                self.logger.debug (message + "\t".join (exceptionStrings))
                self.logger.warning ("Service %s skipped." % serviceName)

    def __loadControllers (self):
        for plugin in self.context.PluginManager ().plugins ("/Controllers"):
            # Each plugin lives in his own context, with his own logger.
            pluginContext = Context (self.context)
            name = plugin.implementation.__name__
            self.logger.message ("Controller %s loaded." % name)
            pluginContext.addService (Logger (name))
            try:
                controller = plugin.createInstance (pluginContext)
                controller.options = plugin.options
                self.controllers.append (controller)
            except Exception, e:
                message = "An error was found while loading the controller: %s." % name
                exceptionStrings = traceback.format_exception (sys.exc_type, 
                                                               sys.exc_value, 
                                                               sys.exc_traceback)
                self.logger.debug (message + "\t".join (exceptionStrings))
                self.logger.warning ("Controller %s not activated." % name)

#    @templatepage
#    def templateErrorHandler(self):
#        return {} # the dict may contain parameters passed to templateErrorHandler.tmpl
    def handle_error(self,systemId=107):
        # idea taken from http://www.cherrypy.org/wiki/ErrorsAndExceptions,
        # systemId can be used to specify category for users
        # here he known codes: 100-None, 101-Framework,102-Look,103-Security,104-Graphics,
        # 105-SiteDB, 106-Prodrequest, 107-support, 108-DBS Discovery
        cherrypy.response.status = 500
#        exc_msg = traceback.format_exc()
        exc_msg = getExcMessage()
        variables={'systemId':systemId,'msg':exc_msg}
#        msg=self.templateErrorHandler()
        msg=str(Template(templateErrorHandler.templateDef,searchList=[variables]))
        cherrypy.response.body = [msg]
        log(cherrypy._cperror.format_exc(),1)
        self.logger.error(cherrypy._cperror.format_exc())
#        sendMail('error@domain.com', 'Error in your web app', _cperror.format_exc())

    def mountControllers (self):
        for controller in self.controllers:
           
            cherrypy.tree.mount (controller,
                                 script_name=controller.options["baseUrl"], 
                                 config=controller.config)
        pass

    def outputConfigMap(self):
        """Log server configuration parameters"""
        serverVars = [
                      'instance',
                      'interrupt',
                      'max_request_body_size',
                      'max_request_header_size',
                      'protocol_version',
                      'ssl_certificate',
                      'ssl_private_key',
                      'socket_host',
                      'socket_port',
                      'socket_file',
                      'reverse_dns',
                      'socket_queue_size',
                      'thread_pool',
                     ]
        msg="+++ CherryPy serer configuration:"
        print msg
        for var in serverVars:
            msg="    %s: %s" % (var, getattr(cherrypy.server,var))
            print msg
        for k,v in cherrypy.config.iteritems():
            msg="    %s: %s" % (k,v)
            print msg
  

    def start (self):
        (opts, args) = self.context.OptionParser ().parse_args ()
        baseUrl, defaultPage = opts.baseUrl, opts.defaultPage
        class DefaultPage (object):
            def __call__ (*args, **kwds):
                raise cherrypy.HTTPRedirect(baseUrl.strip("/") + defaultPage)
            exposed=True
        cherrypy.tree.mount (DefaultPage ())
        self.context.Logger ().debug ("parsed options: %s" % opts)
        if opts.secureRedirect:
            cherrypy.request.hooks.attach ("before_request_body", HttpsOnlyFilter (opts.secureRedirect))
        for controller in self.controllers:
            controller.readyToRun ()
        cherrypy.config.update ({"server.environment": opts.environment})
        # don't use autoreload since it's buggy, see
        # http://trac.cherrypy.org/ticket/902
        cherrypy.config.update ({'engine.autoreload_on': False})
        cherrypy.config.update ({"server.socket_port": int (opts.port)})
        cherrypy.config.update ({"server.socket_host": '0.0.0.0'})
        cherrypy.config.update ({'request.show_tracebacks': False})
        cherrypy.config.update ({'request.error_response': self.handle_error})
# if I add this lines traling problem will go away on front-ends,
# but AJAX calls will fail sinccne they'll want instead of method name, e.g. getSites
# the full path, e.g. dbs_discovery/getSites
#        cherrypy.config.update ({'tools.trailing_slash.on' : True})
#        cherrypy.config.update ({'tools.trailing_slash.missing' : False})
        cherrypy.config.update ({'tools.proxy.on': True})
        cherrypy.config.update ({'tools.proxy.base': '%s' % opts.baseUrl})
#        cherrypy.config.update ({'tools.proxy.local': ''})
        cherrypy.config.update ({'log.screen':True})

        print "CALL BONSAI opts", opts
        if  opts.ssl:
            if  os.environ.has_key('BONSAI_CA'):
                CA  = os.environ['BONSAI_CA']
            else:
                CA  = '/etc/grid-security/hostcert.pem'
            if  os.environ.has_key('BONSAI_KEY'):
                KEY = os.environ['BONSAI_KEY']
            else:
                KEY = '/etc/grid-security/hostkey.pem'
            sdict = {'environment':'production',
                     'server.ssl_certificate': CA,
                     'server.ssl_private_key': KEY}
            cherrypy.config.update(sdict)

        self.outputConfigMap()

        cherrypy.server.quickstart ()
        cherrypy.engine.start ()
