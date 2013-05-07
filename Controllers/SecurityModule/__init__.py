from Framework.Controller import xmlBooleanResponse, exposeSerialized 
from Framework.Controller import require_args
from Tools.Functors import AlwaysFalse
from Tools.Functors import ValueProxy
from Tools.Functors import FetchFromArgs
from Framework import templatepage
from Framework import Controller
from Framework.Logger import Logger
from datetime import datetime, timedelta
from time import strptime, strftime
from Modules.Utilities.Serializers.XML import PythonDictSerializer
from Framework.PluginManager import DeclarePlugin
from Framework.Application import Application
from os import getenv
from Tools.SecurityModuleCore import RedirectorToLogin
from Tools.SecurityModuleCore import Group, Role
from Tools.SecurityModuleCore import SecurityToken
from Tools.SecurityModuleCore.SecurityDBApi import SecurityDBApi
from Tools.SecurityModuleCore import encryptCookie
from Tools.SecurityModuleCore import is_authenticated, is_authorized, NotAuthenticated
from Crypto.Cipher import Blowfish
from base64 import b64encode, b64decode
import crypt

try:
    from cherrypy import expose, request
    import cherrypy
except ImportError:
    pass

class SecurityModule (Controller):
    def __init__ (self, context):
        self.context = context
        Controller.__init__ (self, context, __file__)
        self.security_api = SecurityDBApi (context)
        self.context.addService (self.security_api)
        self.context.addService (Logger ("SECURITY_MODULE_CONTROLLER"))
        
    def readyToRun (self):
        pass
 
    @templatepage
    def login (self, requestedPage="../Studio/login", **args):#FIXME: Get the real requested page
        # VK: requested page is truncated at first &, all parameters passed via args, put them back
        for key in args.keys():
            requestedPage+="&%s=%s"%(key,args[key])
#        raise cherrypy.HTTPRedirect ("/base/SecurityModule/loginReal?requestedPage=%s" % requestedPage)
#        raise cherrypy.HTTPRedirect (self.context.CmdLineArgs ().opts.baseUrl + "/SecurityModule/loginReal?requestedPage=%s" % requestedPage)
        return {'requestedPage': requestedPage}

    @expose
    def loginReal (self, requestedPage, **args):#FIXME: Get the real requested page
        # VK: requested page is truncated at first &, all parameters passed via args, put them back
        for key in args.keys():
            requestedPage+="&%s=%s"%(key,args[key])
        return self.templatePage ("login", {'requestedPage': requestedPage})
    
    @templatepage
    @require_args ("user", "password", "requestedPage", onFail=RedirectorToLogin)
    def authenticate (self, user, password, requestedPage="../Studio/login"): #FIXME: Get the real requested page
        #TODO: adapt to the new schema.
        self.context.Logger().message("Trying to authenticate %s" % user)
        passwdEntry = self.security_api.getPasswordFromUsername (user)
        if not passwdEntry.has_key (0):
            return {'redirect': requestedPage}
        encryptedPassword = passwdEntry[0]['passwd'] 
        #if request.headers['Ssl-Client-S-Dn'] != '(null)':
            #context.Logger().message("Authenticated by certificate")
            #context.Logger().message(request.headers['Ssl-Client-S-Dn'])
            #user = self.security_api.getUsernameFromDN(request.headers['Ssl-Client-S-Dn'])[0]['username']   
        if encryptedPassword == crypt.crypt (password, encryptedPassword):
            self.context.Logger().message("Valid password for user %s" % user)
            cherrypy.response.cookie['dn'] = encryptCookie (user, self.security_api)
            cherrypy.response.cookie['dn']['path'] = '/'
            cherrypy.response.cookie['dn']['max-age'] = 3600*24
            cherrypy.response.cookie['dn']['version'] = 1
            datetimeCookie = strftime("%Y-%m-%dT%H:%M:%S", datetime.now ().timetuple ())
            cherrypy.response.cookie['authentication_time'] = encryptCookie (datetimeCookie, self.security_api)
            cherrypy.response.cookie['authentication_time']["path"] = '/'
            cherrypy.response.cookie['authentication_time']['max-age'] = 3600*24
            cherrypy.response.cookie['dn']['version'] = 1
            cherrypy.response.cookie['originator_hash'] = encryptCookie ("some_hash", self.security_api)
            cherrypy.response.cookie['originator_hash']['path'] = '/'
            cherrypy.response.cookie['originator_hash']['max-age'] = 3600*24
            cherrypy.response.cookie['originator_hash']['version'] = 1
            return {'redirect': requestedPage}
        return {'redirect': requestedPage}
    
    @templatepage
    def logout (self, redirect="../SecurityModule/login", *args, **kw):
        # VK: requested page is truncated at first &, all parameters passed via args, put them back
        for key in kw.keys():
            redirect+="&%s=%s"%(key,kw[key])
        cherrypy.response.cookie['dn'] = encryptCookie ("guest", self.security_api)
        cherrypy.response.cookie['dn']['path'] = '/'
        cherrypy.response.cookie['dn']['max-age'] = 3600*24
        cherrypy.response.cookie['dn']['version'] = 1
        datetimeCookie = strftime("%Y-%m-%dT%H:%M:%S", datetime.now ().timetuple ())
        cherrypy.response.cookie['authentication_time'] = encryptCookie (datetimeCookie, self.security_api)
        cherrypy.response.cookie['authentication_time']["path"] = '/'
        cherrypy.response.cookie['authentication_time']['max-age'] = 3600*24
        cherrypy.response.cookie['dn']['version'] = 1
        cherrypy.response.cookie['originator_hash'] = encryptCookie ("some_hash", self.security_api)
        cherrypy.response.cookie['originator_hash']['path'] = '/'
        cherrypy.response.cookie['originator_hash']['max-age'] = 3600*24
        cherrypy.response.cookie['originator_hash']['version'] = 1
        return {'redirect': redirect}
    
    @exposeSerialized (serializer = PythonDictSerializer ('user'))
    def userInfo (self, *args, **kw):
        #TODO: add a query to get the DN from the id.
        token = SecurityToken ()
        return {"dn": token.dn}
    
    @expose
    @is_authorized (Role ("Global Admin"), Group ("global"), onFail=RedirectorToLogin ("../SecurityModule/login"))
    def becomeUser (self, username, requestedPage, **args):
        cherrypy.response.cookie['dn'] = encryptCookie (username, self.security_api)
        cherrypy.response.cookie['dn']['path'] = '/'
        cherrypy.response.cookie['dn']['max-age'] = 3600*24
        cherrypy.response.cookie['dn']['version'] = 1
        datetimeCookie = strftime("%Y-%m-%dT%H:%M:%S", datetime.now ().timetuple ())
        cherrypy.response.cookie['authentication_time'] = encryptCookie (datetimeCookie, self.security_api)
        cherrypy.response.cookie['authentication_time']["path"] = '/'
        cherrypy.response.cookie['authentication_time']['max-age'] = 3600*24
        cherrypy.response.cookie['dn']['version'] = 1
        cherrypy.response.cookie['originator_hash'] = encryptCookie ("some_hash", self.security_api)
        cherrypy.response.cookie['originator_hash']['path'] = '/'
        cherrypy.response.cookie['originator_hash']['max-age'] = 3600*24
        cherrypy.response.cookie['originator_hash']['version'] = 1
        return self.templatePage ("authenticate", {'redirect': requestedPage})
    
    @expose
    @is_authenticated (onFail=NotAuthenticated)
    def checkIfAuthenticated (self):
        return "This page can be seen only if you are authenticated."
    
    @expose
    @is_authorized (Role ("Global Admin"), Group ("global"), onFail=NotAuthenticated)
    def checkIfAuthorized (self):
        return "This page can be seen only if you are authorized."

    @expose
    def getMasthead(self):
        pass
    
DeclarePlugin ("/Controllers/WebTools/Security", SecurityModule, {"baseUrl": "/SecurityModule"})
