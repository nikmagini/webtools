"""
Service to load the SecurityModule into the context of other applications
"""

from Tools.SecurityModuleCore.SecurityDBApi import SecurityDBApi
from Tools.SecurityModuleCore import RedirectorToLogin, RedirectToLocalPage, RedirectAway
from Tools.SecurityModuleCore import SecurityToken, SecurityTokenFactory, CherryPySecurityTokenImpl
from Framework.PluginManager import DeclarePlugin
from Framework.Context import Context
from Framework.Logger import Logger

class SecurityModuleService (object):
    def __init__ (self, context):
        self.context = context
        childContext = Context (context)
        childContext.addService (Logger ("SecurityDBApi"))
        self.securityApi = SecurityDBApi (childContext)
        self.securityTokenFactory = SecurityTokenFactory (childContext, CherryPySecurityTokenImpl)
        self.siteDBApi = self.securityApi.api
        context.addService (self.securityApi)
        context.addService (self.siteDBApi)
        context.addService (self.securityTokenFactory)
        RedirectorToLogin.context = staticmethod (lambda : self.context)
        RedirectToLocalPage.context = staticmethod (lambda : self.context)
        RedirectAway.context = staticmethod (lambda : self.context)
        
    
    def __del__ (self):
        self.context.Logger ().debug ("About to close DB")
        self.siteDBApi.close ()
        self.context.Logger ().debug ("Done")
        self.context.removeService ("SecurityDBApi")
        self.context.removeService ("SiteDBApi")
        self.context.removeService ("SecurityTokenFactory")

DeclarePlugin ("/Services/SecurityModuleService", SecurityModuleService ,{})