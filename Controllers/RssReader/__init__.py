from Framework.Controller import Controller, templatepage, templateXML
from Framework.PluginManager import DeclarePlugin
from cherrypy import expose

from pysqlite2 import dbapi2 as sqlite
import feedparser 

from Tools.SecurityModuleCore import SecurityToken, RedirectToLocalPage, RedirectAway, RedirectorToLogin
from Tools.SecurityModuleCore import Group, Role, NotAuthenticated, FetchFromArgs
from Tools.SecurityModuleCore import is_authorized, is_authenticated, has_site
from Tools.Functors import AlwaysFalse

#from Framework.Context import Context
#from Tools.SecurityModuleCore import SecurityTokenFactory, DummySecurityTokenImpl

class RssReader (Controller):
    
    feeds_url = ['url1', 'url2']    
    feeds_list = {}    
 
    def __init__ (self, context):
        Controller.__init__ (self, context, __file__)

    @expose
    #@is_authenticated (onFail=RedirectorToLogin("../login"))
    def feedsServer(self, feedsNumber=None, feedsFrequency=None, requestParamethers=None):
        
        if feedsNumber and feedsNumber=="-1":
            return "fn=3"
        elif feedsNumber and int(feedsNumber)>-1:
            return "fn="+feedsNumber
	else:
            if feedsFrequency and feedsFrequency=="-1":
                return "ff=10"
            elif feedsFrequency and int(feedsFrequency)>-1:
                return "ff="+feedsFrequency
            else:
        	#return self.exampleFeed()
                return self.getFeeds(1)

    @templatepage
    def index (self):
        return {}
    
    @templateXML
    def exampleFeed (self, feedsNumber=None, feedsFrequency=None, requestParamethers=None):
        "Return an example feed file. ignoring the arguments"
        return {}

    @expose
    def getFeeds (self, user):
        urls = self.getURLS(user)
        ml = self.mergeFeeds(urls)
        ol = self.orderFeeds(ml)
        return ol.encode('utf-8')

    @expose
    def getURLS (self, id):
        # Add some useable default 
        output = ['http://www.guardian.co.uk/rss','http://www.theregister.co.uk/excerpts.rss']
        # This should be configurable somehow, either environment variable, config file or argument to the method
        try:
            connection = sqlite.connect('/usr/local/sqlite/var/users.db')
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM urls WHERE urls.ID in (SELECT registration.url FROM user, registration WHERE user.ID==registration.user AND user.ID=='+str(id)+')')
            output = []
            for row in cursor:
                output.append(str(row[1]))
        except:
            pass
        return output

    def orderFeeds (self, merged_list=None):
        ordered_list = []
        keys = merged_list.keys()
        keys.sort()
        keys.reverse()
         
        for k in keys:
            ordered_list.append(merged_list[k])
        tmp = ", ".join(ordered_list)
        ordered_list = "{'feeds':["+tmp+"]}"
        return ordered_list

    def mergeFeeds (self, feeds_list=None):
        merged_list = {}
        for url in feeds_list:
            f = feedparser.parse(url)
            source = f.feed.link
            for i in range(len(f['entries'])):
                e = f['entries'][i]
                t = self.getEscapedString(e.title)
                c = self.getEscapedString(e.description)
                l = e.link
                d = str(e.updated_parsed[2])+"-"+str(e.updated_parsed[1])+"-"+str(e.updated_parsed[0])
                h = self.getString(e.updated_parsed[3])+":"+self.getString(e.updated_parsed[4])+":"+self.getString(e.updated_parsed[5])
                s = source
		k = self.getKey(e.updated_parsed, merged_list)
                json = "{'source':'"+s+"', 'title':'"+t+"', 'content':'"+c+"', 'link':'"+l+"', 'date':'"+d+"', 'time':'"+h+"'}"
                merged_list[k] = json
        return merged_list

    def getKey (self, date, merged_list):
        Y = str(date[0])
        M = self.getString(date[1])
        D = self.getString(date[2])
        h = self.getString(date[3])
        m = self.getString(date[4])
        s = self.getString(date[5])       
        key = Y+M+D+h+m+s+'000'
        while (merged_list.has_key(key) == 1):
            k = int(key)
            k = k + 1
            key = str(k)
        return key

    def getString (self, n):
        if (len(str(n))==2):
            return str(n)
        else:
            return '0'+str(n)

    def getEscapedString (self, str):
        return str.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")


DeclarePlugin ("/Controllers/RssReader", RssReader, {"baseUrl": "/RssReader"})
