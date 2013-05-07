#!/usr/bin/env python
"""
__Scruncher__

Scruncher returns java script and/or css from a static directory, after 
minimising setting appropriate headers, etags and gzipping the content if the 
client can accept it.  

TODO: pull in zip files for libraries (config option for url?) and read files 
into the cache from the zip file, e.g.:

from zipfile import Zipfile
yui = zipfile.ZipFile('yui_2.8.0r4.zip', 'r')
yui.namelist()
f = yui.open('yui/build/connection/connection_core-min.js', 'r')
return f.read()
"""

__revision__ = "$Id: Scruncher.py,v 1.4 2010/02/05 13:28:50 metson Exp $"
__version__ = "$Revision: 1.4 $"

import cherrypy
from cherrypy import expose, log, response, tools, HTTPError
from cherrypy import config as cherryconf
from cherrypy.lib.static import serve_file
import cssutils
from jsmin import jsmin
# Factory to load pages dynamically
from WMCore.WMFactory import WMFactory
# Logging
import WMCore.WMLogging
import logging, os, sys
from WMCore.WebTools.Page import Page, exposejs, exposecss

def truefalse(value):
    return str(value).upper() not in ('FALSE', 'N', 'NO')

def setHeaders(type, size=0):
    if size > 0:
        response.headers['Content-Length'] = size
    response.headers['Content-Type'] = type
    response.headers['Expires'] = 'Sat, 14 Oct 2017 00:59:30 GMT'
            
class Scruncher(Page):
    """
    A class to serve appropriately compressed javascript and css from a UI 
    library
    """
    def __init__(self, config):
        """
        Inherit the base class and set up the cache and our loaders
        """
        Page.__init__(self, config)
        self.cache = {'css': {}, 'js':{}, 'image':{}}
        #minify the css
        cssutils.ser.prefs.useMinified()
        # a dictionary of functions to deal with loading different scripts
        #TODO: pick this up from configuration
        #TODO: allow for versioning here, e.g. if YUI3 is very different to YUI2
        self.loaders = {'js': {'yui': yui_ecmascripts},
                        'css': {'yui': yui_style},
                        'image': {'yui': yui_images}}
    @expose
    def index(self):
        response = """<h1>StaticScruncher index:</h1>
<ul>
    <li>style loads from <a href='css'>css</a></li>
    <li>javascript loads from <a href='js'>js</a></li>
    <li>images loads from <a href='images'>images</a></li>
</ul>

<h2>Some examples:</h2>

<ul>CSS
    <li><a href='css/yui-2.8.0/?menu/assets/menu-core.css&menu/assets/menu.css'>Minified YUI Menu CSS</a></li>
    <li><a href='css/yui-2.8.0/?menu/assets/menu-core.css&menu/assets/menu.css&minify=False'>Unminified YUI Menu CSS</a></li>
</ul>
<ul>JS
    <li><a href='js/yui-2.8.0/treeview/progressbar/?minify=False'>Unminified treeview and progressbar</a></li>
    <li><a href='js/yui-2.8.0/treeview/progressbar/?debug=True'>Debug treeview and progressbar</a></li>
    <li><a href='js/yui-2.8.0/treeview/progressbar/'>Minified treeview and progressbar</a></li>
    <li><a href='js/yui-2.8.0/progressbar/treeview/'>Minified progressbar and treeview</a></li>    
    <li><a href='/js/yui-2.8.0/?treeview/treeview-debug.js&/menu/menu-min.js'>Treeview debug and menu minified</a></li>
</ul>
<ul>Image
    <li><img src='images/yui-2.8.0/?menu/assets/menu_down_arrow.png'/></li>
    <li><img src='images/yui-2.8.0/?/slider/assets/bg-fader.gif'/></li>
</ul>

<h2>Cached Data:</h2>
"""     
        cachesize = 0
        for k, v in self.cache.iteritems():
            r = "<ul><b>%s</b>" % k
            for kk, vv in v.iteritems():
                r += "<li><i>%s</i> = %s bytes</li>" % (kk, len(vv))
                cachesize += len(vv)
            r += "</ul>"
            response += r
        response += "<b>Total cache size =</b> %s bytes" % cachesize
        return response
    @expose
    def default(self, *args, **kwargs):
        return self.index()

    @expose
    def images(self, *args, **kwargs):
        """
        serve static images
        """
        ctype = 'png'
        if len(args) > 1:
            ctype = args[1].split('.')[1]
        elif len(kwargs.keys()) > 0:
            kw = kwargs.keys()
            #Remove pesky meaningless debug and minify arguments
            for ky in ['debug', 'minify']:
                if ky in kw:
                    kw.remove(ky)
            ctype = kw[0].split('.')[1]
            
        data = self.return_cache_response(args, kwargs, 'image')
        setHeaders(ctype, len(data))
        return data
    
    @exposecss
    @tools.gzip()
    def css(self, *args, **kwargs):
        """
        cat together the specified css files and return a single css include
        get css by calling: /controllers/css/file1/file2/file3
        """
        mimetypes = ['text/css']
        cherryconf.update({'tools.encode.on': True, 
                           'tools.gzip.on': True
                          })
        
        data = self.return_cache_response(args, kwargs, 'css')
        setHeaders(mimetypes, len(data))
        return data
        
    @exposejs
    @tools.gzip()
    def js(self, *args, **kwargs):
        """
        cat together the specified js files and return a single js include
        get js by calling: /controllers/js/file1/file2/file3
        """
        mimetypes = ['application/javascript', 'text/javascript',
                      'application/x-javascript', 'text/x-javascript']
        cherryconf.update({'tools.gzip.on': True,
                           'tools.encode.on': True,
                          })
        data = self.return_cache_response(args, kwargs, 'js')
        setHeaders(mimetypes, len(data))
        return data
        
    def return_cache_response(self, args, kwargs, extenstion):
        lib_name = args[0]
        args = list(args[1:])
        args.sort()
        cachekey = '+'.join(args)
        cachekey += '+'.join(kwargs.keys())
        # try to minify by default, can explicitly turn this off by setting 
        # ?minify=false
        debug = truefalse(kwargs.get('debug', False))
        minify = truefalse(kwargs.get('minify', True))
        
        if debug:
            cachekey += '+debug'
        elif minify:
            cachekey += '+min'
        if not self.cache[extenstion].has_key(cachekey):
#            #return the cached response
#            print '*****************************'
#            print '* returning cached response *'
#            print '*****************************'
#            print cachekey
#        else:
            # which library am I serving?
            library = self.config.library.section_(lib_name)
            
            data = self.loaders[extenstion][library.type](library.root, 
                                                    minify, 
                                                    debug, args, kwargs)
            # Store to the cache
            self.cache[extenstion][cachekey] = data
        return self.cache[extenstion][cachekey]

def cssmin(css):
    """
    Minify CSS using the cssutils library. 
    """
    sheet = cssutils.parseString(css)
    return sheet.cssText


# Define functions for dealing with YUI. If we need to add another library, or 
# YUI changes significantly we address that by extending/adding new functions
# here.

def crawl_yui_files(script, scriptpath, debug, minify, min_func, extenstion):
    """
    Crawl the YUI file structure and load up the files we need
    """
    filepath = os.path.join(scriptpath, script + extenstion)
    optfilepath = None
    # do we want to load the option file? 
    option = debug & minify
    if debug:
        optfilepath = os.path.join(scriptpath, script + '-debug' + extenstion)
    elif minify:
        optfilepath = os.path.join(scriptpath, script + '-min' + extenstion)
    
    data = ""
    if option and os.path.exists(optfilepath):
        # I should minify/debug and the -min.js/-debug.js exists
        optfile = open(optfilepath)
        data = "".join ([data, optfile.read()])
        optfile.close()
    elif minify and os.path.exists(filepath):
        # I should minify but the -min.js file is missing 
        # I can't add in -debug flags
        origfile = open(filepath)
        data = "".join ([data, min_func(origfile.read())])
        origfile.close()
    elif os.path.exists(filepath):
        # the minify/debug are off so return the unadulterated file
        origfile = open(filepath)
        data = "\n".join ([data, origfile.read()])
        origfile.close()
    else:
        # Sorry the file you requested is not available
        raise HTTPError(404, '%s not found' % filepath)
    return data

def imgmin(image):
    return image

def yui_images(root, minify, debug, args, kwargs):
    """
    Return images from the YUI release, only take a path
    """
    for script in kwargs.keys():
        # There are genuine kwargs that could come in here, so skip them
        if kwargs[script] == '':  
            path_elems = script.split('/')
            script = path_elems[-1]
            scriptpath = os.path.join(root, *path_elems[:-1])
            return crawl_yui_files(script, scriptpath, debug, 
                                    minify, imgmin, '')
    

def yui_style(root, minify, debug, args, kwargs):
    """
    Check that files exist and are minified. Minify scripts which aren't 
    minified if the minify flag is True, ignores the debug flag.
    """
#    YUI places css files in directories called 'assets'. These directories 
#    contain css files as well as other content (images, swf). The css files are
#    not consistently namespaced, for instance the treeview assets do all begin 
#    with treeview, while the tabview assets contains border_tabs.css, and the      
#    asset directory may also contain skins (e.g. /treeview/assets/skins/sam/).
#    This loader assumes you give a path relative to the library root for the 
#    css file you wish to load.
    scripts = kwargs.keys()
    
    data = ''
    for script in scripts:
        # There are genuine kwargs that could come in here, so skip them
        if kwargs[script] == '':            
            path_elems = script.split('/')
            script = path_elems[-1].replace('.css', '')
            scriptpath = os.path.join(root, *path_elems[:-1])
            data += crawl_yui_files(script, scriptpath, debug, 
                                    minify, cssmin, '.css').strip()

    return data.replace('\n', '')

def yui_ecmascripts(root, minify, debug, scripts, kwargs):
    """
    Check that files exist and are minified. Minify scripts which aren't 
    minified if the minify flag is True, return the -debug version of the 
    scripts if debug is True, this automatically prevents minification.
    
    This function allows implicit URL's such as:
    
    localhost:8020/js/yui-2.8.0/treeview/progressbar/yuiloader-dom-event/
    
    and explicit URL's such as:
    
    localhost:8020/js/yui-2.8.0/?treeview/treeview-debug.js&/menu/menu-min.js
    
    For explicit URL's the debug/min options will be honoured, e.g. the above 
    URL will return the minified menu and debug enabled treeview. If -debug/-min
    are not included the minify and debug values passed into the function will 
    be used.
    """
    
    data = ''
    for script in scripts:
        # YUI places scripts in ROOT/script-name
        scriptpath = os.path.join(root, script)
        data += crawl_yui_files(script, scriptpath, debug, minify, jsmin, '.js')

    for script in kwargs.keys():
        # There are genuine kwargs that could come in here, so skip them
        if kwargs[script] == '':            
            path_elems = script.split('/')
            script = path_elems[-1].replace('.js', '')
            s_debug = script.endswith('-debug') | debug
            s_minify = script.endswith('-min') | minify 
            scriptpath = os.path.join(root, *path_elems[:-1])
            data += crawl_yui_files(script, scriptpath, s_debug, 
                                    s_minify, jsmin, '.js').strip()

    return data.replace('\n', '')