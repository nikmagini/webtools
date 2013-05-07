from Framework import Controller, StaticController
from Framework.PluginManager import DeclarePlugin
from Framework.Controller import templateJS, templatepage
from Tools.YUICache import YUICache
import os
import urllib
import sys
import cherrypy
from cherrypy import expose

def setHeaders(type, size=0):
    if size:
        cherrypy.response.headers['Content-Length'] = size
    cherrypy.response.headers['Content-Type'] = type
    cherrypy.response.headers['Expires'] = 'Sat, 14 Oct 2017 00:59:30 GMT'
    
class Common (Controller):
  def __init__ (self, context):      
    Controller.__init__ (self, context, __file__)
    
  @templateJS
  def masthead (self):
    setHeaders('js')
    return {}
    
  @templateJS
  def masthead_table(self):
    setHeaders('js')
    return {}
    
  @expose  
  def mastheadcss(self, site=None, *args, **kwargs):
    files = ['dmwt_main.css', 'dmwt_masthead.css']
    if site:
      files+= ['dmwt_masthead_%s.css' % site]
    path = __file__.rsplit('/',1)[0]
    data = ""
    for f in files:
      filename = "%s/css/%s" % (path, f)
      if os.path.exists(filename):
        lines = file(filename).readlines()
        for l in lines:
          data = data + l

    setHeaders('css')
    return self.templatePage ('data', {'data':data})
  
  @expose  
  def mastheadcss_table(self, site=None, *args, **kwargs):
    files = ['dmwt_main_table.css', 'dmwt_masthead.css']
    if site:
      files+= ['dmwt_masthead_table_%s.css' % site]
    path = __file__.rsplit('/',1)[0]
    data = ""
    for f in files:
      filename = "%s/css/%s" % (path, f)
      if os.path.exists(filename):
        lines = file(filename).readlines()
        for l in lines:
          data = data + l

    setHeaders('css')
    return self.templatePage ('data', {'data':data})
  
  @templatepage
  def help(self):
    return {}
  
  @templatepage
  def datatransfer(self):
    return {}
  
# TODO: Write FAQ template, and later FAQ system  
#  @templatepage
#  def faq(self):
#    return {}

    
class YUI (Controller):
    def __init__ (self, context):
        Controller.__init__ (self, context, __file__)
        # BAD!!!!! Should really use the context for this kind of stuff.
        self.__yuiDir = os.environ["YUI_ROOT"]
        self.__cache = YUICache (self.__yuiDir)
        
    #TODO: Add in backwards compatibility
    #TODO: Could make this the index
    #TODO: Return the files in the right order, regardless of how they are requested
    #TODO: Fill in missing files from dependancy tree
    #FIXME: In case of missing file should raise an HTTP error.
    @expose
    def yui(self, *args, **kwargs):
        """cat together the YUI include files and return a single js include
           get css by calling: /YUI/yui/css/?script=/container/assets/menu/assets/menu.css
           get js by calling: /YUI/yui/js/?script=yahoo.js"""
        data = ''
        if 'script' in kwargs.keys():
            assetType = args[0]
            scripts = []
            if type(kwargs['script']) == type('str'):
                scripts = [kwargs['script']]
            else:
                scripts = kwargs['script']
            for f in scripts:
                content = self.__cache.getContentByLabel (f)
                if not content:
                    raise cherrypy.HTTPError(404)
                data = "\n".join ([data, content.data]);
            setHeaders (content.contentType)
            cherrypy.config.update ({'tools.encode.on': True, 
                                     'tools.gzip.on': True})
            return self.templatePage ('data', {'data': data})

        if len (args) == 1:
            content = self.__cache.getContentByLabel (args[0])
            setHeaders (content.contentType, content.lenght)
            return content.data
        raise cherrypy.HTTPError(404)
            
class MastheadService (object):
    def __init__ (self, context):
        context.addService (self)
        
class FooterService (object):
    def __init__ (self, context):
        context.addService (self)        
        
    def includes (self):
        return """
<script type="text/javascript" src="../YUI/yui/yahoo"></script>
<script type="text/javascript" src="../YUI/yui/connection"></script> 
"""

DeclarePlugin ("/Controllers/Common", Common, options={"baseUrl": '/Common'})
DeclarePlugin ("/Controllers/YUI", YUI, options={"baseUrl": "/YUI"})
DeclarePlugin ("/Services/MastheadService", MastheadService, {})
DeclarePlugin ("/Services/FooterService", FooterService, {})

