from Framework import Context
from Framework.Logger import Logger
from Framework.Controller import xmlBooleanResponse, exposeSerialized 
from Framework.Controller import require_args
from Framework import templatepage
from Framework.PluginManager import DeclarePlugin
from Framework.Application import Application
from Framework import Controller

from Tools.Functors import AlwaysFalse
from Tools.Functors import ValueProxy
from Tools.Functors import FetchFromArgs
from Modules.Utilities.Serializers.XML import PythonDictSerializer

from Tools.SiteDBCore import SiteDBApi

from cherrypy import expose, HTTPRedirect, request

from datetime import datetime, timedelta
from time import strptime, strftime

from os import getenv

from Crypto.Cipher import Blowfish
from base64 import b64encode, b64decode
import crypt
import traceback
import random

class RedirectAway (object):
    import cherrypy
    def __init__ (self, page):
        self.page = page
    def __call__ (self, *args, **kwds):
        raise HTTPRedirect(self.page)

class RedirectToLocalPage (object):
    def __init__ (self, page):
        self.page = page
    def __call__ (self, *args, **kwds):
        self.baseUrl = self.context().CmdLineArgs ().opts.baseUrl
        raise HTTPRedirect("%s%s" % (self.baseUrl, self.page))
    
class RedirectorToLogin (object):
    def __init__ (self, page):
        #FIXME: get self.page from the referrer
        self.page = page
    def __call__ (self, *args, **kwds):
        self.baseUrl = self.context().CmdLineArgs ().opts.baseUrl
        url = "%s/SecurityModule/login?requestedPage=%s" % (self.baseUrl, self.page)
        raise HTTPRedirect(url)

def NotAuthenticated (*args, **kw):
    return "I could show you this web page, but then I would have to kill you..."

def redirectionToSiteDB(userDN):
    page = """<div style="font-size:12px;font-family: helvetica, arial, verdana, sans-serif;font-weight: normal;">"""
    page+= "We found your user DN: %s<br/><br/>"%str(userDN)
    page+= "But we were unable to lookup your user name in SiteDB.<br /><br />"
    page+= """Please use the following link to correct your Personal information over there: SiteDB <a href="https://cmsweb.cern.ch/sitedb/people/showAllEntries" style="color:red">link</a>.<br /><br/>"""
    page+= "Once this is done we'll be able to use your certificate to authenticate for various CMS services.<br /><br/>"
    page+= """If you need further assistance please use this twiki <a href="https://twiki.cern.ch/twiki/bin/view/CMS/SiteDBForCRAB">page</a>"""
    page+= "</div>"
    return page

def is_authenticated (onFail=NotAuthenticated):
    def decorator (function):
        context = Context ()
        context.addService (Logger ("SECURITY_MODULE"))
        def wrapper (self, *__args, **__kw):
            # Check if there is a user.
            token = SecurityToken ()
            context.Logger().message("Checking authentication for user %s" % (token.dn) )

            # NOTE: this part should be clarified once front-end/back-end
            # certificate-based auth. rules will be in place
            # so we we should just fail over to login/pw schema
            ### If user browser provide cert, extract this info and update token
            userDN = ""
            try:
                import cherrypy,time
#                print "###",cherrypy.request.headers
#                userDN  = cherrypy.request.headers['Ssl-Client-S-Dn']
#                access  = cherrypy.request.headers['Ssl-Client-Verify']
#                if  userDN!='(null)' and access=='SUCCESS':
                userDN  = cherrypy.request.headers['Cms-Client-S-Dn']
                access  = cherrypy.request.headers['Cms-Auth-Status']
                if  userDN!='(null)' and access=='OK':
                    context.Logger().message("Found DN in user certificate")
                    # SiteDB usees token.dn as username rather then DN itself, so name is misleading
                    userName = self.securityApi.getUsernameFromDN(userDN)[0]['username']
                    token.impl.dn = userName
#                    token.impl.dn = userDN
                    aTime = time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime())
                    token.impl.authenticationTime = aTime
            except:
#                traceback.print_exc()
                # redirect to https://cmsweb.cern.ch/sitedb/people/showAllEntries
#                return redirectionToSiteDB(userDN)
                pass

            if token.dn in (None, "guest"):
                return onFail (self)
            # Check that the session has not expired.
            if not token.authenticationTime:
                return onFail (self)
            authenticationTime = datetime(*strptime(token.authenticationTime, "%Y-%m-%dT%H:%M:%S")[0:6])
            currentTime = datetime.now ()
            # TODO: this should come from the configuration file.
            maxPeriod = timedelta (seconds=3600*24)
            if authenticationTime + maxPeriod < currentTime:
                context.Logger().message("Cookie has expired, authorisation failed.")
                return onFail (self)
            return function (self, *__args, **__kw)
        return wrapper
    return decorator

def is_authorized (role=FetchFromArgs ("role"), region=FetchFromArgs("region"), onFail=AlwaysFalse()):    
  def decorator (function):
      context = Context ()
      context.addService (Logger ("SECURITY_MODULE"))
      def wrapper (self, *__args, **__kw):
          api = self.context.SecurityDBApi ()          
          fetchedRole = role (*__args, **__kw)
          fetchedRegion = region (*__args, **__kw)
          token = SecurityToken ()

          # NOTE: this part should be clarified once front-end/back-end
          # certificate-based auth. rules will be in place
          # so we we should just fail over to login/pw schema
          ### If user browser provide cert, extract this info and update token
          userDN = ""
          try:
              import cherrypy,time
#              print "###",cherrypy.request.headers
#              userDN  = cherrypy.request.headers['Ssl-Client-S-Dn']
#              access  = cherrypy.request.headers['Ssl-Client-Verify']
#              if  userDN!='(null)' and access=='SUCCESS':
              userDN  = cherrypy.request.headers['Cms-Client-S-Dn']
              access  = cherrypy.request.headers['Cms-Auth-Status']
              if  userDN!='(null)' and access=='OK':
                  context.Logger().message("Found DN in user certificate")
                  # SiteDB usees token.dn as username rather then DN itself, so name is misleading
#                  print userDN,access
#                  print self.securityApi.getUsernameFromDN(userDN)
                  userName = self.securityApi.getUsernameFromDN(userDN)[0]['username']
                  token.impl.dn = userName
#                  token.impl.dn = userDN
                  aTime = time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime())
                  token.impl.authenticationTime = aTime
          except:
#              traceback.print_exc()
              # redirect to https://cmsweb.cern.ch/sitedb/people/showAllEntries
#              return redirectionToSiteDB(userDN)
              pass

          context.Logger().message("""Checking authorization for user %s to be %s in region %s """ % (token.dn, fetchedRole, fetchedRegion) )
          # Check that the session has not expired.
          if not token.authenticationTime:
              return onFail (self)
          authenticationTime = datetime(*strptime(token.authenticationTime, "%Y-%m-%dT%H:%M:%S")[0:6])
          currentTime = datetime.now ()
          # TODO: this should come from the configuration file.
          maxPeriod = timedelta (seconds=3600*24)
          context.Logger().message("checking if is_authorized")
          if authenticationTime + maxPeriod < currentTime:
              context.Logger().message("Cookie has expired, authorisation failed.")
              return onFail (self, *__args, **__kw) 
          if token.dn == None:
              context.Logger().message("No DN, authorisation failed.")
              return onFail (self, *__args, **__kw)                   
          elif api.hasGroupResponsibility (token.dn, fetchedRegion, fetchedRole):
              context.Logger().message("Granted group responsibility")
              return function (self, *__args, **__kw)
          elif api.hasSiteResponsibility (token.dn, fetchedRegion, fetchedRole):
              context.Logger().message("Granted site responsibility")
              return function (self, *__args, **__kw)
          else:
              context.Logger().message("Authorisation failed.")
              return onFail (self, *__args, **__kw)
      wrapper.__name__ = function.__name__
      return wrapper
  return decorator  


def has_role (role=FetchFromArgs ("role"), onFail=AlwaysFalse()):
    def decorator (function):
        def wrapper (self, *__args, **__kw):
            fetchedRole = role (*__args, **__kw)
            token = SecurityToken ()
            print "Checking if user %s has role %s" % (token.dn, fetchedRole) 
#            if fetchedRole == None:
#                return onFail (self)           
            if self.context.SecurityDBApi ().hasRole (token.dn, fetchedRole):
                print "Permission granted"
                return function (self, *__args, **__kw)
            else:
                return onFail (self, *__args, **__kw)
        wrapper.__name__ = function.__name__
        return wrapper
    return decorator

def has_site (site=FetchFromArgs ("site"), onFail=AlwaysFalse()):
    def decorator (function):
        def wrapper (self, *__args, **__kw):
            print __kw
            fetchedSite = site (*__args, **__kw)
            token = SecurityToken ()
            print "Checking if user %s has site %s" % (token.dn, fetchedSite)      
#            if fetchedSite == None:
#                return onFail (self, *__args, **__kw)
            if self.context.SecurityDBApi ().hasSite (token.dn, fetchedSite):
                print "Permission granted"
                return function (self, *__args, **__kw)
            else:
                return onFail (self, *__args, **__kw)
        wrapper.__name__ = function.__name__
        return wrapper
    return decorator

def has_group (group=FetchFromArgs ("group"), onFail=AlwaysFalse()):
    def decorator (function):
        def wrapper (self, *__args, **__kw):
            fetchedGroup = group (*__args, **__kw)
            token = SecurityToken ()
            print "Checking if user %s has group %s" % (token.dn, fetchedGroup) 
#            if fetchedGroup == None:
#                return onFail (self)           
            if self.context.SecurityDBApi ().hasGroup (token.dn, fetchedGroup):
                print "Permission granted"
                return function (self, *__args, **__kw)
            else:
                return onFail (self, *__args, **__kw)
        wrapper.__name__ = function.__name__
        return wrapper
    return decorator

def check_ownership (objIdSelector, ownershipCheker, onFail=AlwaysFalse):
    def decorator (function):
        def wrapper (self, *__args, **__kw):
            if ownershipCheker (context=self.context, entry=objIdSelector(*__args, **__kw)):
                return function (self, *__args, **__kw)
            return onFail ()
        return wrapper
    return decorator


#What are these for???
ciphers_cache = {}
current_key = None
last_key_id = 0

class Group (ValueProxy):
    pass

class Role (ValueProxy):
    pass

def decryptCookie (cryptedCookie, security_api):
    global ciphers_cache
    global current_key
    global last_key_id
    keyId, cryptedInfo = cryptedCookie.split ("|")
    try:
        cipher = ciphers_cache[keyId]
    except KeyError:
        key = b64decode (security_api.getCryptoKey (keyId)['key'])
        cipher = Blowfish.new (key)
        ciphers_cache[last_key_id] = cipher
        last_key_id += 1
    return cipher.decrypt (b64decode (cryptedInfo)).strip ("\x08")

def encryptCookie (value, security_api):
    global ciphers_cache
    global current_key
    global last_key_id
    if current_key == None:
        current_key_plain = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for x in xrange(10)])
        cryptkey = b64encode (current_key_plain)
        currentKeyId = security_api.addCryptoKey (key=cryptkey)
    try:
        cipher = ciphers_cache[currentKeyId]
    except KeyError:
        key = b64decode (cryptkey)
        cipher = Blowfish.new (key)
        ciphers_cache[last_key_id] = cipher
        last_key_id += 1
    while len (value) % 8:
        value += "\x08"
    return "%s|%s" % (currentKeyId, b64encode(cipher.encrypt (value)))

class EmptySecurityTokenImpl (object):
    def __init__ (self, context):
        self.dn = None
        self.authenticationTime = None
        self.originatorHash = None
        self.userId = None

class DummySecurityTokenImpl (object):
    def __init__ (self, context):
        self.dn = "admin"
        self.authenticationTime = None
        self.originatorHash = None
        self.userId = 0
        
class EnvironmentSecurityTokenImpl (object):
    def __init__ (self, context):
        if getenv ("USERDN"):
            self.dn = getenv ("USERDN")
            self.authenticationTime = getenv ("AUTHENTICATION_TIME")
            self.originatorHash = getenv ("ORIGINATOR_HASH")
            self.userId = getenv ("USERID")

class CherryPySecurityTokenImpl (object):
    def __init__ (self, context):
        self.security_api = context.SecurityDBApi ()
        try:
            import cherrypy
            cookie = cherrypy.request.cookie
            try:
                self.dn = decryptCookie (cookie["dn"].value, self.security_api)
                self.authenticationTime = decryptCookie (cookie["authentication_time"].value, self.security_api)
                self.originatorHash = decryptCookie (cookie["originator_hash"].value, self.security_api)
                return
            except KeyError:
                self.dn = 'Unknown' 
                self.authenticationTime = None
                self.originatorHash = None
        except ImportError:
            context.Logger ().message ("Cannot use CherryPySecurityTokenImpl")
            pass
        except AttributeError:
            pass

    def __getUserId (self):
        users = self.security_api.getUsernameFromDN(self.dn)
        for user in users:
            return user.id
        return None
    userId = property (__getUserId, None, None, "Returns the id, as provided by the security module.")

        
# TODO: use plugin labels rather than specify the tokenImpl directly.
class SecurityTokenFactory (object):
    def __init__ (self, context, tokenImpl):
        self.context = context
        self.tokenImpl = tokenImpl
        SecurityToken.context = staticmethod (lambda : context)
        SecurityToken.factory = staticmethod (lambda : self)
    
    def createToken (self):
        return self.tokenImpl (self.context)
    
class SecurityToken (object):
    """ This is just a wrapper class to abstract the SecurityToken functionalities.
        The actual implementation is provided by the concrete classes instanciated by the 
        SecurityToken factory.
        A simple, standalone version of the SecurityToken should do the following:
        
        from Framework.Context import Context
        from Tools.SecurityModuleCore import SecurityTokenFactory, DummySecurityTokenImpl
        
        context = Context ()
        context.addService (SecurityTokenFactory (context, DummySecurityTokenImpl))
        token = SecurityToken ()
    """
    def __init__ (self):
        # Notice that the SecurityToken class is injected the "factory ()" staticmethod by the  
        # SecurityTokenFactory itself in order to avoid percolating the context to the token.
        # This is done in order to be able to use the security class even in things that do not
        # have a context.
        self.impl = self.factory ().createToken ()

    def __getUserId (self):
        return self.impl.userId 
    
    def __getDN (self):
        return self.impl.dn
    
    def __getAuthenticationTime (self):
        return self.impl.authenticationTime
    
    def __getOriginatorHash (self):
        return self.impl.originatorHash
    
    userId=property(__getUserId, None, None, "Returns the userId associated to the token.")
    dn=property (__getDN, None, None, "Returns the dn associated to the token")
    authenticationTime=property (__getAuthenticationTime, None, None, "Returns the authentication time associated to the token")
    originatorHash=property (__getOriginatorHash, None, None, "Returns the originatorHash associated to the token")
