#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
# Author:  Valentin Kuznetsov, 2008

"""
Webtools base controller. It is used to serve masthead, JavaScript
and CSS files for cmsweb cluster.
"""

import cherrypy
import os
import string
import traceback

from cherrypy import expose
from Framework import Controller
from Framework.PluginManager import DeclarePlugin

from Framework import Context
from Framework.Logger import Logger

# This service should starts as
# cmsWeb --base-url=https://vocms33.cern.ch/base --port=7999 --default-page /WSServer/
# cmsWeb --base-url=https://cmsweb.cern.ch/base --port=7999 --default-page /WSServer/

class WSServer(Controller):
    """
    Webtools-base server code. All functionality is done in Controller class
    from which we inherit.
    """
    def __init__(self,context=""):
        """Constructor"""
        self.masthead = None
        self.footer   = None
        self.baseUrl  = None
        try:
            Controller.__init__ (self, context, __file__)
        except:
            raise traceback.format_exc()

    def readyToRun(self):
        """Define parameters for this service which are passed from cmsWeb"""
        opts=self.context.CmdLineArgs().opts
        self.baseUrl = opts.baseUrl
#        self.masthead=self.baseUrl+"/Common/masthead"
#        self.footer=self.baseUrl+"/Common/footer"
        self.masthead="/base/Common/masthead"
        self.footer="/base/Common/footer"

    @expose
    def index(self):
        """Method to display content of web page for this service"""
        request = cherrypy.request
        print request.headers
        print request.base
        print "baseUrl :",self.baseUrl
        print "masthead:",self.masthead
        print "footer  :",self.footer
        page = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head profile="http://www.w3.org/2005/11/profile">
<title>CMS File Server</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta http-equiv="Content-Language" content="en-us" />
<meta name="author" content="Valentin Kuznetsov (vkuznet at gmail dot com)" />
<meta name="MSSmartTagsPreventParsing" content="true" />
<meta name="ROBOTS" content="ALL" />
<meta name="Copyright" content="(CC) 2008, CMS collaboration." />
<meta http-equiv="imagetoolbar" content="no" />
<meta name="Rating" content="General" />

<link rel="stylesheet" type="text/css" href="/base/Common/mastheadcss?site=help"/>

<script type="text/javascript" src="/base/YUI/yui/js/?script=yahoo.js&script=dom.js&script=event.js&script=container_core.js&script=connection.js&script=dragdrop.js&script=container.js"></script>
<script type="text/javascript" src="/base/Common/masthead"></script>
<script type="text/javascript">
function footerMenuText(){
        return [
{label: "Home", link: "", title: "home page"},
    ]

}
</script>
<body onload="insertMastHead('help',' TEST::test')" id="content">
TEST PAGE
</body>
</html>
"""
        return page

# declare Controller to be invoke within cmsWeb
DeclarePlugin ("/Controllers/base/WSServer", WSServer, {"baseUrl": "/WSServer"})
