"SiteDB pages"
from Framework.PluginManager import DeclarePlugin
from Framework import Controller, StaticController, templatepage
from Tools.Functors import AlwaysFalse
from Tools.SiteDBCore import SiteDBApi, SiteResources, SiteSurvey, SAM
from Tools.SecurityModuleCore.SecurityDBApi import SecurityDBApi
from Tools.SecurityModuleCore import SecurityToken, RedirectToLocalPage, RedirectAway, RedirectorToLogin
from Tools.SecurityModuleCore import Group, Role, NotAuthenticated, FetchFromArgs
from Tools.SecurityModuleCore import is_authorized, is_authenticated, has_site
from os import getcwd, listdir
from os.path import join, exists
from os import getenv

# TODO: Get this to work, build numpy et al in Web tools
#from graphtool.web.bonsai import GraphMixIn

import urllib
import ConfigParser
import sys
import os
import re
import time, calendar, datetime

from cherrypy import expose, HTTPRedirect, request 

def siteDBNotAuthenticated (*args, **kw):
        args[0].context.Logger().message("Unauthenticated access atempted")
        args[0].context.Logger().debug(request.headers)
        page = args[0].context.CmdLineArgs().opts.baseUrl + request.request_line.split()[1]
        return args[0].templatePage ("SiteDBNotAuthenticated",{"page":page})
    
def return_type (returnType):
        def decorator (func):
            import cherrypy
            def wrapper (*args, **kwds):
                    cherrypy.response.headers['Content-Type'] = returnType
                    return func (*args, **kwds)
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            return wrapper
        return decorator

#TODO: Set global flag if import of security stuff fails to import
#TODO: Get software list via ajax callback

class Page(Controller):
  database = ''
  dbtype = ''
  title = 'Untitled Page'
  basepath = ''
  db = ''
  baseurl = ''
  #TODO: Gather statistics
    
class SiteDBCfg(object):
    templatesPath = staticmethod (lambda : join (__file__.rsplit ("/", 1)[0], "Templates"))

class SiteDB(Page):
    context = ""

    def __init__ (self, context):
        self.context = context
        Controller.__init__ (self, context, __file__)
        self.basepath = __file__.rsplit('/', 1)[0]
        self.context.addService (SiteDBCfg())
        self.context.addService (SecurityDBApi (context))

    def readyToRun (self):
        cfgFilename = self.context.CmdLineArgs().opts.cfgFilename
        if not exists(cfgFilename):
            defaultConfig = ConfigParser.ConfigParser ()
            defaultConfig.add_section ("endpoint")
            defaultConfig.set ("endpoint", "phedex", "https://cmsdoc.cern.ch:8443/cms/test/aprom/phedex/tbedi/Request::Create?dest=")
            defaultConfig.set ("endpoint", "dbs", "http://cmsdbs.cern.ch/discovery/getBlocksFromSiteHelper?dbsInst=MCGlobal/Writer&site=")
            defaultConfig.set ("endpoint", "goc", "https://goc.grid-support.ac.uk/gridsite/gocdb2/index.php?siteSelect=")
            defaultConfig.set ("endpoint", "gstat", "http://goc.grid.sinica.edu.tw/gstat/")
            defaultConfig.set ("endpoint", "dashboard", "http://lxarda16.cern.ch/dashboard/request.py")
            defaultConfig.set ("endpoint", "sam", "http://www-ekp.physik.uni-karlsruhe.de/~rabbertz/cmsmon/web/cmsmon_site.php?")
            defaultConfig.set ("security", "cert", '/home/cmsweb/certificate/hostcert.pem')
            defaultConfig.set ("security", "key", '/home/cmsweb/certificate/hostkey.pem')
            defaultConfig.write (file (cfgFilename, 'w'))
            self.context.Logger ().message ("Default sitedb.ini created.")
        config = ConfigParser.ConfigParser()
        config.read (cfgFilename)
        self.context.Logger ().message ("Get DB")
        self.db = self.context.SiteDBApi ()
        self.context.Logger ().message (self.db.connectionType ()) 
        self.dbtype = self.db.connectionType ()    
        #TODO: get self.baseurl from context throughout
        self.baseurl = self.context.CmdLineArgs().opts.baseUrl
        self.context.addService (config)
     
class Admin(SiteDB):
    @is_authorized (Role("Global Admin"), Group("global"), 
                    onFail=RedirectToLocalPage ("/sitelist/"))
    def index(self):
      #Add/set CMS names
      return self.templatePage('Admin', {'db':self.db, 'context':self.context})
    index.exposed = True
    
    @is_authorized (Role("Global Admin"), Group("global"), 
                    onFail=RedirectToLocalPage ("/sitelist/"))
    def edit(self, *args, **kwargs):
      return self.templatePage('Admin_Edit', {'db':self.db, 'args':args, 'kwargs':kwargs, 'dbtype': self.dbtype, 'context':self.context})
    edit.exposed = True
    
class Test(SiteDB):    
  @templatepage
  def helloAgain(self):
      fields = {}
      fields = ['id', 'name', 'tier']
      select = "select id, name, tier from site order by tier, name"
      person = {'name': 'roger', 'id': 1}
      dict = {'thing1': person, 'thing2': 'pete'}
      #data = self.db.getDataObject(fields, select)
      data = request.headers
      return {'helloString': "Hello world", 'fields': fields, 'select': select, 'dict': dict, 'data':data}
  helloAgain.expose = True
  
  @is_authorized (Role("Production Operator"), Group("production"), onFail=RedirectAway ("http://localhost:8030/sitedb/test/helloAgain"))
  def securityTest(self):
      self.context.Logger().message("In Security test")    
      fields = {}
      fields = ['id', 'name', 'tier']
      select = "select id, name, tier from site order by tier, name"
      person = {'name': 'roger', 'id': 1}
      dict = {'thing1': person, 'thing2': 'pete'}
      data = self.db.getDataObject(fields, select)

      return self.templatePage('helloAgain', {'helloString': "Secure Hello world", 'fields': fields, 'data': data, 'select': select, 'dict': dict})
  securityTest.exposed = True
  
  def index(self):
      fields = {}
      fields = ['id', 'name', 'tier']
      select = "select id, name, tier from site order by tier, name"
      data = self.db.getDataObject(fields, select)
      for d in data:
          for f in fields:
              self.context.Logger().message( "%s: %s" % (f, data[d][f]))
          self.context.Logger().message("----")
  index.exposed = True  
#class Site(SiteDB, GraphMixIn):

class Site(SiteDB):
    siteResult = ""
    parentsResult = ""
    childrenResult = ""
    resourcesResult = ""
    ceList = ''
    seList = ''
    admin = True
            
    def contacts(self, site = None):
        #TODO: Move to template
        outputstring = ""
        persondict = self.db.getSitePersonDict(site)
        if len(persondict) == 0:
            outputstring = "<p>No site contacts</p>"
        else:
            people = persondict.keys()
            people.sort()
            outputstring = "<dl>"
            for p in people:
                roles = persondict[p]['roles'].keys()
                rolelist = ''
                for r in roles:
                    rolelist += '"' + persondict[p]['roles'][r] + '" '
                outputstring += '''
                <dt><a href="mailto:%s">%s</a></dt>
                <dd><b>%s</b> <br/> tel 1: %s, tel 2: %s</dd>''' % (persondict[p]['email'], persondict[p]['name'], 
                                                                                          rolelist, persondict[p]['phone1'], persondict[p]['phone2'])

            outputstring += '''
            </dl>'''
                
        return outputstring

    def associations(self, site = None):
        #Fill the following div's from the DB, for loop
        types = ('parent', 'child')
        assocstring = ''
        string = ''
        for t in types:
            asites=self.db.getAssociatedSites(site, t)
            if len(asites) == 0:
                string = ""
            else:
                string = '''
        <div class="box">        
            <h6>%s Sites</h6>
            <ul>''' % t.title() #Make first letter of t Upper case
                for s in asites:
                    string += '''
                <li><a href="%s/site/?site=%s">%s</a></li>''' % (self.baseurl, asites[s]['id'], asites[s]['name'])
                string += '''
            </ul>
        </div>'''
            assocstring += string

        if len(assocstring) > 0:    
            return '''
        <h3>Associated Sites</h3>
%s
                ''' % (assocstring)
        else:
            return '''
            <h3>Associated Sites</h3>
            <div class="box">
            <p>No Associated Sites</p>
            </div>
            '''
    
    @is_authenticated (onFail=siteDBNotAuthenticated)
    def configuration(self, show=None, site = None, siteinfo = None):
        if siteinfo == None:
            siteinfo = self.db.getSiteInfo(site)[0]
        # TODO:  Avoid wasteful multiple round trips to DB
        resource={}
        for t in ('CE','SE', 'SQUID'):
            resource[t] = self.db.getResource(site, t)
        nodes = self.db.getPhEDExNodes(site)
        return self.templatePage ("Site_index_configuration", {'resource': resource, 
                                                               'siteinfo': siteinfo,
                                                               'nodes': nodes,
                                                               'goc': siteinfo['gocid'],
                                                               'config': self.context.ConfigParser(),
                                                               'token': SecurityToken()})
    configuration.exposed = True
    
   # @is_authenticated (onFail=siteDBNotAuthenticated)     
    def software(self, site = None, siteinfo = None):
        if siteinfo == None:
            siteinfo = self.db.getSiteInfo(site)[0]
        celist = self.db.getResource(siteinfo['id'], 'CE')
        software = {}
        pins = {}
        for c in celist:
            #Get the list of software from SAM
            endpoint = self.context.ConfigParser().get("endpoint", "sam")
            cert = self.context.ConfigParser().get("security", "cert")
            key = self.context.ConfigParser().get("security", "key")
            software[celist[c]['fqdn']] = []
            try:
                software[celist[c]['fqdn']] = SAM(endpoint, cert, key).getCMSSWInstalls(celist[c]['fqdn'])
            except Exception, e:
                self.context.Logger().error(e)
                self.context.Logger().error("Couldn't access SAM results from %s" % endpoint)
            # Get a list of pinned software for the CE
            select = "select release, arch from pinned_releases where ce_id = :ce"
            binds = { 'ce' : celist[c]['id'] }
            data = self.db.getDataObject(['release', 'arch'], select, binds)
        
            pins[celist[c]['fqdn']] = {}
            for d in data:
                if data[d]['arch'] in pins[celist[c]['fqdn']].keys():
                    pins[celist[c]['fqdn']][data[d]['arch']].append(data[d]['release'])
                else:
                    pins[celist[c]['fqdn']][data[d]['arch']] = [data[d]['release']]
            #pins[celist[c]['fqdn']] = {'slc3_ia32_gcc323':[],
            #           'slc4_ia32_gcc345':['CMSSW_1_6_0', 'CMSSW_1_2_9']}
            self.context.Logger ().debug( pins )
        return self.templatePage ("Site_index_software", {'siteinfo': siteinfo,
                                                          'software': software,
                                                          'pins': pins})
    software.exposed = True

    @is_authenticated (onFail=siteDBNotAuthenticated)                
    def toparea(self, siteinfo = None, show = 'yes', site = None):
        if siteinfo == None:
            siteinfo = self.db.getSiteInfo(site)[0]
        return self.templatePage ("Site_index_toparea", {'show': show, 
                                                         'siteinfo': siteinfo, 
                                                         'siteid':site,
                                                         'token': SecurityToken()})    
    toparea.exposed = True
#    
#    def plottest(self):
#        data = {'foo':45, 'bar':55}
#        metadata = {'title':'Hello Graphing World!'}
#        graphName = "PieGraph"
#        return self.templateGraph( graphName, data, metadata )
#    plottest.exposed = True
    
    @is_authenticated (onFail=siteDBNotAuthenticated)     
    def index(self, site = None):
        if site != None:
            if not site.isdigit():
                #site is the site name, not the id
                fields = {}
                fields['siteid'] = ['id', 'name']
                select = "select id, name from site where name = :site"
                binds = { 'site' : site }
                data = self.db.getDataObject(fields['siteid'], select, binds)
                site = data[0]['id']
        #TODO: set site by CMS name, GOC ID, BDII name etc.
        #TODO: These relationships as a report
        siteinfo = self.db.getSiteInfo(site)
        types = ('CE','SE')
        resource={}
        resstring={}
        # TODO:  Avoid wasteful multiple round trips to DB
        for t in types:
            resource[t] = self.db.getResource(site, t)
            resstring[t] = ''
            for r in resource[t]:
                resstring[t] += resource[t][r]['fqdn'] + ', '
            resstring[t] = resstring[t].rstrip(', ')
        nodes = self.db.getPhEDExNodes(site)
        now = datetime.datetime.now()
        then = now + datetime.timedelta(weeks=-1)
        now = time.mktime(now.timetuple())
        then = time.mktime(then.timetuple())
        if len(siteinfo) > 0:
            return self.templatePage ("Site_index",{'siteinfo': siteinfo[0],
                                                    'id': site,
                                                    'software': self.software(siteinfo = siteinfo[0], 
                                                                              site = site),
                                                    'now': now,
                                                    'then': then,
                                                    'tiers': self.db.getTierList(),
                                                    'config': self.context.ConfigParser(),
                                                    'toparea': self.toparea(siteinfo = siteinfo[0],
                                                                                  site = site),
                                                    'contacts':self.contacts(site), 
                                                    'configuration': self.configuration(siteinfo = siteinfo[0],
                                                                                        site = site), 
                                                    'associations': self.associations(site),
                                                    'phedexnodes':nodes,
                                                    'resources': resstring,
                                                    'token': SecurityToken()})
        else:
            return self.templatePage ("SiteDB_error", {'msg': 'Something went wrong!', 'redirect': 'None'})
    
    index.exposed = True
    
class SiteList(SiteDB):
    title = "Site Directory"
    
    @is_authenticated (onFail=siteDBNotAuthenticated)    
    def addNewSite(self):
        return self.templatePage ("SiteList_add",{'token': SecurityToken()})
    
    addNewSite.exposed = True
    
    @is_authenticated (onFail=siteDBNotAuthenticated)  
    def deleteSite(self):
        return self.templatePage ("SiteList_delete",{'sitelist': self.db.getSiteList(),
                                                    'token': SecurityToken()})
    deleteSite.exposed = True

    @is_authenticated (onFail=siteDBNotAuthenticated)     
    def index(self, naming_scheme="cmsname"):
        
        names = {"name":"Site Name",
                 "cmsname":"CMS Site Name",
                 "lcgname":"WLCG Site Name",
                 "phedex":"PhEDEx Node Name",
                 "ce":"Compute Element",
                 "se":"Storage Element"}
        order = ["name", "cmsname", "lcgname", "phedex", "ce", "se"]
        return self.templatePage ("SiteList_index",{'title': self.title, 
                                                    'scheme': naming_scheme,
                                                    'names': names,
                                                    'order': order,
                                                    'sitelist': self.db.getSiteList(naming_scheme),
                                                    'token': SecurityToken()})
    
    index.exposed = True

#TODO: Edit person - given email address or DN

class People(SiteDB):
    title = "Person Directory"

    @is_authenticated (onFail=siteDBNotAuthenticated)     
    def showAllEntries(self, site = None, all = False, initial = 'A'):
        fields={}
        data = ''
        if site == None or all:
            fields['person'] = ['id', 'surname', 'forename', 'email', 'dn', 'username', 'phone1', 'phone2']
            select = """select id, surname, forename, email, dn, username, phone1, phone2 from contact 
            where upper(surname) like :firstletter 
            order by upper(surname)"""
            data = self.db.getDataObject(fields['person'], select, {'firstletter': '%s%%' % initial})
        else:
            fields['person'] = ['id', 'surname', 'forename', 'email', 'dn', 'username', 'phone1', 'phone2']
            select = """
            select distinct
                contact.id, contact.surname, contact.forename, contact.email, contact.dn, contact.username, contact.phone1, contact.phone2  
            from  site_responsibility
                join contact on contact.id = site_responsibility.contact
                join site on site.id = site_responsibility.site
            where site.id = :site"""
            
            binds = {'site' : site}
            data = self.db.getDataObject(fields['person'], select, binds)    
        return self.templatePage ("People_showAllEntries", {'data': data, 
                                                          'fields': fields['person'], 
                                                          'token': SecurityToken(),
                                                          'site': site,
                                                          'all': all})
    showAllEntries.exposed = True

    def edit(self, id = None, site=None, ajax = None):
        if self.context.SecurityDBApi().hasSiteResponsibility(SecurityToken().dn, site, "Site Executive|Site Admin|Data Manager") or self.context.SecurityDBApi().hasGroupResponsibility(SecurityToken().dn, "global","Global Admin"):
            fields = ['id', 'surname', 'forename', 'email', 'dn', 'phone1', 'phone2', 'username' ]
            select = "select id, surname, forename, email, dn, phone1, phone2, username from contact where id = :id"
            binds = { 'id' : id }
            persondata = self.db.getDataObject(fields, select, binds)[0]
            siteselect = ""
            sitedata = ""
            binds = {}
            if site != None:
                siteselect = """select role.title, site.id
                    from site_responsibility, contact, role, site
                    where contact.id = site_responsibility.contact AND
                    role.id = site_responsibility.role AND
                    site.id = site_responsibility.site AND
                    site.id = :site AND
                    contact.id = :id"""
                binds = { 'id' : id, 'site' : site } 
                sitedata = self.db.getSiteInfo(site)
            else:
                siteselect = """select role.title, site.id
                    from site_responsibility, contact, role, site
                    where contact.id = site_responsibility.contact AND
                    role.id = site_responsibility.role AND
                    site.id = site_responsibility.site AND
                    contact.id = :id"""
                binds = { 'id' : id }
                sitedata = self.db.getSiteListObj()
                site = 0
            personsite = ['role', 'sid']
            assocdata = self.db.getDataObject(personsite, siteselect, binds)
            groupselect = """select count(user_group.id)
            from group_responsibility, contact, role, user_group
            where contact.id = group_responsibility.contact AND
            role.id = group_responsibility.role AND
            user_group.id = group_responsibility.user_group AND
            contact.id = :id AND
             role.title = :role"""
            binds = { 'id' : id , 'role': 'Global Admin'}
            admindata = self.db.getDataObject(['count'], groupselect, binds)
            if admindata[0]['count']:
                assocdata[len(assocdata)] = {'role': 'Global Admin', 'sid': 0}
            roleselect = "select id, title from role where title != 'Global Admin'"
            rolelist = ['id', 'title']
            roledata = self.db.getDataObject(rolelist, roleselect)
            return self.templatePage ("People_edit",{"fields": fields,
                                                 "persondata": persondata,
                                                 "assocdata": assocdata,
                                                 "roledata": roledata,
                                                 "sitedata": sitedata,
                                                 "singlesite": site})
        else:
            RedirectToLocalPage ("/sitedb/people/")
    edit.exposed = True                                                 
 
    @is_authorized (Role("Global Admin"), Group("global"), 
                    onFail=RedirectToLocalPage ("/sitedb/people/"))
    def editgroup(self, id = None, ajax = None):
        fields = ['id', 'surname', 'forename', 'email', 'dn', 'phone1', 'phone2', 'username' ]    
        select = "select id, surname, forename, email, dn, phone1, phone2, username from contact where id = :id"
        binds = { 'id' : id }
        persondata = self.db.getDataObject(fields, select, binds)[0]
        
        groupselect = """select role.title, user_group.id
            from group_responsibility, contact, role, user_group
            where contact.id = group_responsibility.contact AND 
            role.id = group_responsibility.role AND 
            user_group.id = group_responsibility.user_group AND
            contact.id = :id"""
        binds = { 'id' : id }
        personsite = ['role', 'gid']
        assocdata = self.db.getDataObject(personsite, groupselect, binds)
        
        roleselect = "select * from role where id != 1"
        rolelist = ['id', 'title']
        roledata = self.db.getDataObject(rolelist, roleselect)
        
        groupselect = "select id, name from user_group"
        groupdata = self.db.getDataObject(['id', 'name'], groupselect)
        
        return self.templatePage ("People_editgroup",{"fields": fields, 
                                                 "persondata": persondata,
                                                 "assocdata": assocdata,
                                                 "roledata": roledata,
                                                 "groupdata": groupdata})
    editgroup.exposed = True
    
    @is_authenticated (onFail=siteDBNotAuthenticated)
    def editme(self, username = None):
        token = SecurityToken()
        if not token.dn == username:
            raise HTTPRedirect(self.baseurl + "/people/")
        fields = ['id', 'surname', 'forename', 'email', 'dn', 'phone1', 'phone2', 'im_handle', 'username' ]    
        select = "select id, surname, forename, email, dn, phone1, phone2, im_handle, username from contact where username = :username"
        binds = { 'username' : username }
        persondata = self.db.getDataObject(fields, select, binds)[0]
        
        siteselect = """select role.title, role.id as role_id, site.name, site.id as site_id
            from site_responsibility, contact, role, site
            where contact.id = site_responsibility.contact AND 
            role.id = site_responsibility.role AND 
            site.id = site_responsibility.site AND
            contact.username = :username"""
        binds = { 'username' : username }
        
        siteassocdata = self.db.getDataObject(['role', 'role_id', 'name', 'site_id'],
                                              siteselect, binds)
        
        groupselect = """select role.title, role.id, user_group.name, user_group.id
            from group_responsibility, contact, role, user_group
            where contact.id = group_responsibility.contact AND 
            role.id = group_responsibility.role AND 
            user_group.id = group_responsibility.user_group AND
            contact.username = :username"""
        groupassocdata = self.db.getDataObject(['role', 'role_id', 'name', 'group_id'],
                                               groupselect, binds)
                    
        return self.templatePage ("People_editme",{"fields": fields, 
                                             "persondata": persondata,
                                             "siteassocdata": siteassocdata,
                                             "groupassocdata": groupassocdata,
                                             "sitedata": self.db.getSiteListObj()})
    editme.exposed = True
    
    @is_authorized (Role("Global Admin"), Group("global"), 
                    onFail=RedirectToLocalPage ("/sitedb/people/"))    
    def delete(self, id = None, ajax = None):
        fields = {}
        fields['person'] = ['id', 'surname', 'forename', 'email', 'dn', 'phone1', 'phone2']
        select = "select * from contact where id = :id"
        binds = { 'id' : id }
        data = self.db.getDataObject(fields['person'], select, binds)

        entrylist = """<table border="1">
    <tr>
        <td><p class="center">ID</p></td><td><p class="center">Surname</p></td><td><p class="center">Forename</p></td><td><p class="center">Email</p></td><td><p class="center">DN</p></td><td><p class="center">Phone 1</p></td><td><p class="center">Phone 2</p></td>
    </tr>
        """
        for p in data:
            entrylist += """    <tr>"""
            for f in fields['person']:
                entrylist += """        <td><p>%s</p></td>""" % (data[p][f])
            entrylist += """    <tr>"""    
        entrylist += """</table>"""    
        if ajax == 'True':
            return '''                <form method="get" action="%s/editsite/">
                <input type="hidden" value="deleteperson" name="region"/>
                <input type="hidden" value="%s" name="pid"/>
    <h4>Are you sure you want to delete the following entry?</h4>
    %s</form>
    ''' % (self.baseurl, id, entrylist)
        else:
            return self.templatePage ("People_delete",{"id": id, "entrylist": entrylist})
    delete.exposed = True
    
    def addPerson(self, site = 0): # Turn into a panel ajax thing
        if self.context.SecurityDBApi().hasSiteResponsibility(SecurityToken().dn, site, "Site Executive|Site Admin|Data Manager") or self.context.SecurityDBApi().hasGroupResponsibility(SecurityToken().dn, "global","Global Admin"):
            roledata = "None"
            if site != 0:
                # TODO:  Cleverly add this functionality to the DbApi
                roleselect = "select id, title from role where id != 1"
                fields = ['id', 'title']
                roledata = self.db.getDataObject(fields, roleselect)

            return self.templatePage("People_add",{"site": site, 'roles': roledata})
        else:
            RedirectToLocalPage ("/sitedb/people/")
    addPerson.exposed=True

    @is_authenticated (onFail=siteDBNotAuthenticated)
    def index(self, name = None):
        #TODO: Show group and other contacts
        if name == None:
            return self.templatePage ("People_index",{"sitepersondict": self.db.getSitePersonDict(), 
                                                      "grouppersondict": self.db.getGroupPersonDict(),
                                                      "token": SecurityToken()})
        else:
            return self.templatePage ("People_index",{"sitepersondict": self.db.getSitePersonDict(None, name), 
                                                      "grouppersondict": self.db.getGroupPersonDict(None, name),
                                                      "token": SecurityToken()})
    index.exposed = True

class Reports(SiteDB):
    def getReportList(self):
        #TODO: Template!!
        list = '''<form method="get" action="%s/reports/showReport">
<select name="reportid">''' % self.baseurl
        list += '<option>Select report</option>'
        for r in listdir(self.basepath + "/reports/"):
            if os.path.isfile(self.basepath + "/reports/" + r) and r.endswith(".ini"):
                list += '''<option value="%s">%s</option>''' % (r, r.replace("_", " ").replace(".ini","").title())
        list += '''
</select>
<input type="submit" value="Display this report">
</form>'''
        return list

    def getSQLReport(self, sql = None, fields = None, output = None):
        fields = fields.split(', ')
        data =[]
        try:
            data = self.db.getDataObject(fields, sql)
        except:
            self.context.Logger().error("Error processing SQL report")
            self.context.Logger().error(fields)
            self.context.Logger().error(sql)
        report = ''
        for d in data:
            report += "<p>"
            tmp = output
            for f in fields:
                tmp = tmp.replace("$"+f, '%s' % data[d][f])
            report += tmp
            report += "</p>\n"
        return report    
    
    @is_authenticated (onFail=siteDBNotAuthenticated)
    def authReport(self, report=None, config=None):
        result=self.getSQLReport(config.get("report", "statement"), 
                                 config.get("report", "fields"), 
                                 config.get("report", "output"))
        return self.templatePage ("Report_results",{"report": report,
                                                    "config": config, 
                                                    "result":result,
                                                    "reportlist": self.getReportList()})
    
    @is_authenticated (onFail=siteDBNotAuthenticated)
    @return_type ("application/xhtml+xml")
    def authXMLReport(self, report=None, config=None):
        data = self.db.getDataObject(config.get("report", "fields").split(', '), 
                                     config.get("report", "statement"))
        return self.templatePage("Report_results_xml",{'data':data,  
                                                       'config':config})

    def showReport(self, reportid=None):
        config = ConfigParser.ConfigParser()
        config.read(self.basepath + "/reports/" + reportid)
        try:
            restricted = config.get("report", "restricted")
        except Exception, e:
            restricted = "yes"
        #TODO: hide/show sql pane - do in template
        if restricted == 'no':
            result=self.getSQLReport(config.get("report", "statement"), 
                                 config.get("report", "fields"), 
                                 config.get("report", "output"))
            self.context.Logger().message("Showing unrestricted report: %s" % reportid)
            return self.templatePage ("Report_results",{"report": reportid,
                                                        "config": config, 
                                                        "result": result,
                                                        "reportlist": self.getReportList()})
        else:
            self.context.Logger().message("Showing restricted report: %s" % reportid)
            return self.authReport(report=reportid, config=config)
    showReport.exposed = True
    
    @return_type ("application/xhtml+xml")
    def showXMLReport(self, reportid=None):
        config = ConfigParser.ConfigParser()
        config.read(self.basepath + "/reports/" + reportid)
        restricted = config.get("report", "restricted")

        if restricted == 'no':
            self.context.Logger().message("Showing unrestricted report: %s" % reportid)
            data = self.db.getDataObject(config.get("report", "fields").split(', '), 
                                         config.get("report", "statement"))
            return self.templatePage("Report_results_xml",{'data':data,  
                                                           'config':config})
        else:
            self.context.Logger().message("Showing restricted report: %s" % reportid)
            return self.authXMLReport(report=reportid, config=config)
    showXMLReport.exposed = True


    @is_authenticated (onFail=siteDBNotAuthenticated)
    def index(self, reportid=None):
        return self.templatePage ("Report_index",{"body": self.getReportList()}) 
    index.exposed = True

class Resources(SiteDB):
  @is_authenticated (onFail=siteDBNotAuthenticated)
  def index(self, site=None, showquarter=False, quarter=None, year=None):
    if quarter == None or year == None: 
      from datetime import date
      now = date.today()
      year = now.year
      quarter = 0
      for i in xrange(0, 4, 1):
        if now.month in xrange ((3*i) + 1, 1 + (3*(1+i)), 1):
          quarter = i + 1
    
    resources = SiteResources(self.context, site)
    resources.publicResources(quarter, year)   # Populate the public resource pledge
    return self.templatePage ("Resources_index",{'resources': resources, 'year': year,
                                                 'showquarter': showquarter, 'quarter':quarter,
                                                 'sitelist': self.db.getSiteList("name")}) 
            
  index.exposed = True
  
  @is_authenticated (onFail=siteDBNotAuthenticated)  
  def edit(self, site=None, quarter=None, year=None, *args, **kwargs):
    if kwargs:
      if kwargs['siteid']:
        site = kwargs['siteid']
        resources = SiteResources(self.context, site)
        kwargs['year'] = year
        kwargs['quarter'] = quarter
        resources.commit(kwargs)
        raise HTTPRedirect(self.baseurl + '/resources/?site=' + site)
      else:
        return self.templatePage ("SiteDB_error",
                                  {'msg': 'Unknown site. You will be redirected to the Site List page in 5 seconds.',
                                   'redirect': 'sitelist/'})
    else :
      resources = SiteResources(self.context, site)
      resources.publicResources(quarter, year)
      
      self.context.Logger().debug(resources.pledge)
      
      return self.templatePage ("Resources_edit",{'resources': resources,'year': year,
                                                 'quarter':quarter,}) 
          
  edit.exposed = True
    
class EditSite(SiteDB):
    #TODO: Check HTTP referrer is this page
    processRequestBody = True
    @is_authorized (Role("Site Admin|Site Executive"), region=FetchFromArgs("siteid"),
                onFail=RedirectToLocalPage("sitelist"))
    def editTopArea(self, siteid=None, name=None, tier=None, 
                    country=None, usage=None, url=None, logo=None):
        update = """update site
set name = :name, country = :country, usage = :usage,
url = :url, logourl = :logo, tier = :tier
where id = :siteid"""
         
        binds = {"siteid": siteid, "name": name, "country": country,
                 "usage": usage, "url": url, "logo": logo, "tier": tier}
        
        self.db.editDataObject(update, binds)
      
        raise HTTPRedirect(self.baseurl + '/site/toparea?show=no&site=' + siteid)

    @is_authorized (Role("Site Admin|Site Executive|Global Admin|PhEDEx Contact"), region=FetchFromArgs("siteid"), 
                onFail=RedirectToLocalPage("sitelist"))
    def editConfig(self, siteid=None, ce = None, se = None, gocdbid = 0, manual = 'n', devel = 'n', phedex = None):
        #TODO: Finish config update for CE/SE - choose primary
        #TODO: Improve this, store PhEDEx nodes if modified by a phedex admin
        #TODO: Make a clever "if oracle, autoincrement" function to avoid all these cases...
        delete = """delete from resource_element where site = :site"""
        binds = { 'site': siteid }
        self.db.editDataObject(delete, binds)

        insert_sqlite =  """insert into resource_element (site, fqdn, type, is_primary)
                            values (:siteid, :fqdn, :type, :is_primary)"""
        insert_oracle = """insert into resource_element (id, site, fqdn, type, is_primary)
                           values (resource_element_sq.nextval, :siteid, :fqdn, :type, :is_primary)"""
        
        for c in ce.split(', '):
            if len(c) > 0:
                binds = { 'siteid' : siteid, 'fqdn' : c,
                      'type' : 'CE', 'is_primary' : 'n' }
                if self.dbtype == 'sqlite':
                    self.db.editDataObject(insert_sqlite, binds)
                elif self.dbtype == 'oracle' or self.dbtype == 'SQLAlchemy':
                    self.db.editDataObject(insert_oracle, binds)
                else:
                    self.context.Logger().error("Unknown database type '%s'; please use Oracle or SQLite" % self.dbtype)
                    
        for s in se.split(', '):
            if len(s) > 0:
                binds = { 'siteid' : siteid, 'fqdn' : s,
                      'type' : 'SE', 'is_primary' : 'n' }
                if self.dbtype == 'sqlite':
                    self.db.editDataObject(insert_sqlite, binds)
                elif self.dbtype == 'oracle' or self.dbtype == 'SQLAlchemy':
                    self.db.editDataObject(insert_oracle, binds)
                else:
                    self.context.Logger().error("Unknown database type '%s'; please use Oracle or SQLite" % self.dbtype)
            
        update = """update site set getdevlrelease = :devel, manualinstall = :manual, gocdbid = :gocdbid where id = :siteid"""

        binds = {'siteid': siteid, 'devel': devel,
                         'manual': manual,'gocdbid': gocdbid}
        
        self.db.editDataObject(update, binds)
        
        # Update PhEDEx node(s)
        if phedex and phedex != 'None':
            self.context.Logger().message("------------------------")
            self.context.Logger().message("editing PhEDEx nodes")
            self.editPhEDEx(siteid=siteid, phedex=phedex)

        raise HTTPRedirect(self.baseurl + '/site/configuration?show=no&site=' + siteid)

    @is_authorized (Role("Site Admin|Global Admin|PhEDEx Contact"), region=FetchFromArgs("siteid"),
                onFail=NotAuthenticated)    
    def editPhEDEx(self, siteid=None, phedex=None):
    #    siteid=kwargs['siteid']
    #    phedex=kwargs['phedex']
        self.context.Logger().message("editing PhEDEx nodes")
        sql = "select name from phedex_node where site = :site"
        binds = { 'site' : siteid}
        oldnodes = self.db.getDataObject(['node'], sql, binds)
        l = []
        for n in oldnodes:
            l.append(oldnodes[n]['node'])

        oldnodes = set(l)
        phedex = set(phedex.split(','))
        delnodes = oldnodes - phedex
        addnodes = phedex - oldnodes
        
        for n in delnodes:
            delete = "delete from phedex_node where site = :site and name = :node"
            binds = { 'site' : siteid, 'node': n.strip()}
            self.db.editDataObject(delete, binds)
        for n in addnodes:
            insert = ""
            if self.dbtype == 'sqlite':
                insert = "insert into phedex_node (name, site) values (:name, :site)"
            elif self.dbtype == 'oracle':
                insert = "insert into phedex_node (id, name, site) values (site_sq.nextval, :name, :site)"
            binds = { 'site' : siteid, 'name': n.strip()}
            self.db.editDataObject(insert, binds)
    
    def editPerson(self, kwargs):
        fields = {}
        fields['person'] = ['surname', 'forename', 'email', 'dn', 'username', 'phone1', 'phone2', 'im_handle']
        update = """update contact set"""
        for f in fields['person']:
            update += """ %s=:%s,""" %(f, f)
        update = update.rstrip(',')
        update += """ where id = :id"""
        
        DN = 'DN unknown %s' % kwargs['email']
        if kwargs['dn'] != '' and kwargs['dn'] != None:
            DN = kwargs['dn']
            
        IM = 'None'
        if 'im_type' in kwargs.keys() and 'im_handle' in kwargs.keys():
            if kwargs['im_type'] != '' and kwargs['im_type'] != None and kwargs['im_handle'] != '' and kwargs['im_handle'] != None:
                IM = "%s:%s" % (kwargs['im_type'], kwargs['im_handle'])
                
        binds = {'surname': kwargs['surname'], 'forename': kwargs['forename'], 
                 'dn': DN, 'username': kwargs['username'],
                 'phone1': kwargs['phone1'], 'phone2': kwargs['phone2'], 
                 'email': kwargs['email'], 'id': kwargs['id'],
                 'im_handle': IM}
        self.db.editDataObject(update, binds)
        if 'siteassoc' in kwargs > 0:
            "get list of previous site roles and compare to new list"
            if type(kwargs['siteassoc']) == type('str'):
                kwargs['siteassoc'] = [kwargs['siteassoc']]
            
            newroles = set(kwargs['siteassoc'])
        else:
            newroles = set()
        
        select = 'select role, site from site_responsibility where contact = :contact'
        if 'singlesite' in kwargs.keys() and int(kwargs['singlesite']) > 0:
            select = select + ' and site = %s' % kwargs['singlesite']
        oldroles = self.db.getDataObject(['role', 'site'], select, {'contact': kwargs['id']})
                
        l = []
        for r in oldroles:
            l.append('%s_%s' % (oldroles[r]['site'],oldroles[r]['role']))
        oldroles = set(l)
        
        delroles = oldroles - newroles
        addroles = newroles - oldroles
        for r in delroles:
            self.context.SecurityDBApi().rescindUserSiteRole(kwargs['id'], r.split('_')[0], r.split('_')[1])

        for r in addroles:
            self.context.SecurityDBApi().grantUserSiteRole(kwargs['id'], r.split('_')[0], r.split('_')[1])
                
        if 'globaladmin' in kwargs:
            self.grantGlobalAdmin(kwargs)
                
        returnurl = '%s/people/?name=%s %s' % (self.baseurl, kwargs['forename'], kwargs['surname'])
        raise HTTPRedirect(returnurl)
    
    def editPersonGroup(self, kwargs):
        fields = {}
        fields['person'] = ['surname', 'forename', 'email', 'dn', 'username', 'phone1', 'phone2']
        update = """update contact set"""
        for f in fields['person']:
            update += """ %s=:%s,""" %(f, f)
        update = update.rstrip(',')
        update += """ where id = :id"""
        
        DN = 'DN unknown %s' % kwargs['email']
        if kwargs['dn'] != '' and kwargs['dn'] != None:
            DN = kwargs['dn']
        
        binds = {'surname': kwargs['surname'], 'forename': kwargs['forename'], 
                 'dn': DN, 'username': kwargs['username'],
                 'phone1': kwargs['phone1'], 'phone2': kwargs['phone2'], 
                 'email': kwargs['email'], 'id': kwargs['id']}
        self.db.editDataObject(update, binds)
        if 'groupassoc' in kwargs > 0:
            "get list of previous site roles and compare to new list"
            select = 'select role, user_group from group_responsibility where contact = :contact'
            
            oldroles = self.db.getDataObject(['role', 'group'], select, {'contact': kwargs['id']})
            
            if type(kwargs['groupassoc']) == type('str'):
                kwargs['groupassoc'] = [kwargs['groupassoc']]
            
            newroles = set(kwargs['groupassoc'])

            l = []
            for r in oldroles:
                l.append('%s_%s' % (oldroles[r]['group'],oldroles[r]['role']))
            oldroles = set(l)
            
            delroles = oldroles - newroles
            addroles = newroles - oldroles
            for r in delroles:
                self.context.SecurityDBApi().rescindUserGroupRole(kwargs['id'], r.split('_')[0], r.split('_')[1])

            for r in addroles:
                self.context.SecurityDBApi().grantUserGroupRole(kwargs['id'], r.split('_')[0], r.split('_')[1])

        if 'globaladmin' in kwargs:
            self.grantGlobalAdmin(kwargs)
                        
        returnurl = '%s/people/?name=%s %s' % (self.baseurl, kwargs['forename'], kwargs['surname'])
        raise HTTPRedirect(returnurl)

    @is_authorized (Role("Global Admin"), region=FetchFromArgs("siteid"),
                onFail=RedirectToLocalPage("sitelist"))
    def grantGlobalAdmin(self, kwargs):
        select = """select role.id, user_group.id 
        from user_group, role
        where role.title=:sdb_role and user_group.name=:sdb_group"""
        binds = {'sdb_role':'Global Admin', 'sdb_group': 'global'}
        data = self.db.getDataObject(['role', 'group'], select, binds)
        #Remove global admin for contact
        delete = 'delete from group_responsibility where contact = :id and role = :role'
        self.db.editDataObject(delete, {'id' : int(kwargs['id']), 'role' : int(data[0]['role'])})
        if kwargs['globaladmin']:
            insert = '''insert into group_responsibility (contact, user_group, role)
                  values (:sdb_contact, :sdb_group, :sdb_role)'''
            binds = { 'sdb_contact' : int(kwargs['id']),
                      'sdb_group' : int(data[0]['group']),
                      'sdb_role' : int(data[0]['role'])}
            self.db.editDataObject(insert, binds)
            
    # TODO:  Again, clever oracle autoincrement function...
    def addPerson(self, kwargs):
        binds = kwargs.copy()
        try:
            del binds['region']
        except:
            pass
        try:
            del binds['siteassoc']
        except:
            pass
        if not 'surname' in binds: binds['surname'] = ''
        if not 'forename' in binds: binds['forename'] = ''
        if not 'email' in binds: binds['email'] = ''
        if not 'dn' in binds: binds['dn'] = 'Unknown DN %s' % binds['email']
        if not 'username' in binds: binds['username'] = ''
        if not 'phone1' in binds: binds['phone1'] = ''
        if not 'phone2' in binds: binds['phone2'] = ''
        if self.dbtype == 'sqlite':
            insert = """insert into contact (surname, forename, email, dn, username, phone1, phone2)
                        values (:surname, :forename, :email, :dn, :username, :phone1, :phone2)"""
        elif self.dbtype == 'oracle' or self.dbtype == 'SQLAlchemy':
            insert = """insert into contact (id, surname, forename, email, dn, username, phone1, phone2)
                        values (contact_sq.nextval, :surname, :forename, :email, :dn, :username, :phone1, :phone2)"""
        else:
            self.context.Logger().message("Unknown database type '%s'; please use Oracle or SQLite" % self.dbtype)
        try:
            self.db.editDataObject(insert, binds)
            self.context.Logger().message("Added new person!")
        except Exception, e:
            self.context.Logger().error("Failed to insert new contact")
            self.context.Logger().error(insert)
            self.context.Logger().error(binds)
            self.context.Logger().error(e)
            raise HTTPRedirect(self.baseurl + '/people/showAllEntries') 
        outerbinds = {'dn' : binds['dn'], 'email': binds['email'], 'forename': binds['forename'],'surname': binds['surname']}
        outerbinds['id'] = self.db.getDataObject('id', 'select id from contact where dn = :dn and email = :email and forename = :forename and surname = :surname', outerbinds)[0]['id']
       
        if 'siteassoc' in kwargs > 0:    
            self.context.Logger().message("Adding site associations for : %s %s (id %s)" % (outerbinds['forename'], outerbinds['surname'], outerbinds['id']))
            insert = '''insert into site_responsibility (contact, site, role)
                      values (:contact, :site, :role)'''
            
            if type(kwargs['siteassoc']) == type([]):
                for a in kwargs['siteassoc']: 
                    binds = { 'contact' : outerbinds['id'],
                          'site' : a.split('_')[0],
                          'role' : a.split('_')[1] }
                    try:
                        self.db.editDataObject(insert, binds)
                        self.context.Logger().message("Added new association! %s " % binds)
                    except Exception, e:
                        self.context.Logger().error("Failed to insert new contact")
                        self.context.Logger().error(insert)
                        self.context.Logger().error(binds)
                        self.context.Logger().error(e)
            elif type(kwargs['siteassoc']) == type('str'):
                binds = { 'contact' : outerbinds['id'],
                      'site' : kwargs['siteassoc'].split('_')[0],
                      'role' : kwargs['siteassoc'].split('_')[1] }
                try:
                    self.db.editDataObject(insert, binds)
                    self.context.Logger().message("Added new association! %s " % binds)
                except Exception, e:
                    self.context.Logger().error("Failed to insert new contact")
                    self.context.Logger().error(insert)
                    self.context.Logger().error(binds)
                    self.context.Logger().error(e)
            else:
                self.context.Logger().message("Unexpected type for site association: %s" % type(kwargs['siteassoc']))
        # Add person id to query string to edit site association
        raise HTTPRedirect(self.baseurl + '/people/showAllEntries') 
    
    def deletePerson(self, kwargs):
            delete = """delete from contact where id = :id"""
            binds = {}
            binds['id'] = kwargs['pid']
            
            self.db.editDataObject(delete, binds)
            raise HTTPRedirect(self.baseurl + '/people/')

    # TODO:  Again, clever oracle autoinc... I wish I would have just written the damn thing    
    def addSite(self, kwargs):
        insert = []
        binds = []
        if 'sitename' in kwargs.keys() and 'tier' in kwargs.keys() and 'location' in kwargs.keys() and 'cmsname' in kwargs.keys() and 'samname' in kwargs.keys():
            
            if self.dbtype == 'sqlite':
                insert.append("""insert into site (name, tier, country)
                            values (:sitename, :tier, :country)""")
                insert.append("insert into cms_name (name) values (:cms_name)")
                insert.append("insert into sam_name (name) values (:sam_name)")
                insert.append("""insert into phedex_node (site, name) values ((select id from site where name = :sitename),
                 :cms_name)""")
            elif self.dbtype == 'oracle' or self.dbtype == 'SQLAlchemy':
                insert.append("""insert into site (id, name, tier, country)
                            values (site_sq.nextval, :sitename, :tier, :country)""")
                insert.append("insert into cms_name (name, id) values (:cms_name, cms_name_sq.nextval)")
                insert.append("insert into sam_name (name, id) values (:sam_name, sam_name_sq.nextval)")
                insert.append("""insert into phedex_node (site, name, id) values ((select id from site where name = :sitename),
                 :cms_name, phedex_node_sq.nextval)""")
    
            else:
                self.context.Logger().message("Unknown database type '%s'; please use Oracle or SQLite" % self.dbtype)
            insert.append("""insert into sam_cms_name_map (sam_id, cms_name_id) values (
                (select id from sam_name where name = :sam_name), 
                (select id from cms_name where name = :cms_name))""")  
            insert.append("""insert into site_cms_name_map (site_id, cms_name_id) values (
                (select id from site where name = :sitename), 
                (select id from cms_name where name = :cms_name))""")
                        
            binds.append({ 'sitename' : kwargs['sitename'],
                  'tier' : kwargs['tier'],
                  'country' : kwargs['location']})
            binds.append({'cms_name' : kwargs['cmsname']})
            binds.append({'sam_name' : kwargs['samname']})
            binds.append({'sitename' : kwargs['sitename'], 'cms_name' : kwargs['cmsname']})
            binds.append({'sam_name' : kwargs['samname'], 'cms_name' : kwargs['cmsname']})
            binds.append({'sitename' : kwargs['sitename'], 'cms_name' : kwargs['cmsname']})
            
            self.db.editDataObject(insert, binds)
            
            raise HTTPRedirect(self.baseurl + '/site/?site=' + kwargs['sitename'])
        else:
            return "Insufficient parameters. Please complete all form fields"

    def deleteSite(self, kwargs):
        #TODO: What other deletes? Responsibilities...
        binds = { 'siteid' : kwargs['siteid'] }
        delete = """delete from site where id = :siteid"""
        self.db.editDataObject(delete, binds)
        delete = """delete from site_association where parent_site = :siteid"""
        self.db.editDataObject(delete, binds)
        delete = """delete from site_association where child_site = :siteid"""
        self.db.editDataObject(delete, binds)
        delete = """delete from site_responsibility where site = :siteid"""
        self.db.editDataObject(delete, binds)
        delete = """delete from resource_element where site = :siteid"""
        self.db.editDataObject(delete, binds)
        raise HTTPRedirect(self.baseurl + '/sitelist/')
    
    def pinSoftware(self, kwargs):
        #Work out a diff to what is listed in the database and update accordingly
        pindict={}# a dictionary keyed on CE containing a dictionary keyed on arch with a list of releases
        if 'pinned' in kwargs.keys():
            for p in kwargs['pinned']:
                
                pinsToProcess = p.split(';') #['release:CMSSW_1_6_6', 'arch:slc4_ia32_gcc345', 'ce:lcgce01.gridpp.rl.ac.uk']
                ce = pinsToProcess[2].split(':')[1] 
                arch = pinsToProcess[1].split(':')[1]
                release = pinsToProcess[0].split(':')[1]
                if ce in pindict.keys():
                    if arch in pindict[ce].keys():
                        pindict[ce][arch].append(release)
                    else:
                        pindict[ce][arch] = [release]
                else:
                    pindict[ce] = {arch:[release]}
        for ce in pindict.keys():
            select = "select id from resource_element where fqdn = :ce"
            binds = { 'ce' : ce }
            data = self.db.getDataObject(['ce_id'], select, binds)
            ce_id = data[0]['ce_id']
            select = """select release, arch from pinned_releases 
                        where ce_id = :ce
                        order by arch"""
            binds = { 'ce' : ce_id }
            data = self.db.getDataObject(['release', 'arch'], select, binds)
            dbpins = {}
            for d in data:
                if data[d]['arch'] in dbpins.keys():
                    dbpins[data[d]['arch']].append(data[d]['release'])
                else:
                    dbpins[data[d]['arch']] = [data[d]['release']]
            archictectures = set(pindict[ce].keys()) | set(dbpins.keys())
            for arch in archictectures:
                formpins = set([])
                oldpins = set([])
                if arch in pindict[ce].keys():
                    formpins = set(pindict[ce][arch])
                if arch in dbpins.keys():
                    oldpins = set(dbpins[arch])
                for release in formpins - oldpins:
                    #add to database
                    insert = """insert into pinned_releases (ce_id, arch, release) 
                                values (:ce, :arch, :release);"""
                    binds = {'ce':ce_id, 'arch':arch, 'release':release}
                    self.db.editDataObject(insert, binds)
                for release in oldpins - formpins:
                    #remove from database
                    delete = """delete from pinned_releases where ce_id = :ce and arch = :arch and release = :release"""
                    binds = {'ce':ce_id, 'arch':arch, 'release':release}
                    self.db.editDataObject(delete, binds)
            
        raise HTTPRedirect(self.baseurl + '/site/?site=' + kwargs['site'])
            
    @is_authenticated (onFail=siteDBNotAuthenticated)    
    def index(self, *args, **kwargs):
	for k in kwargs.keys():
            if type(kwargs[k]) == type('string'):
                kwargs[k] = urllib.unquote(kwargs[k])
        if kwargs['region'] == 'toparea':
            if not 'name' in kwargs: kwargs['name'] = ''
            if not 'tier' in kwargs: kwargs['tier'] = ''
            if not 'country' in kwargs: kwargs['country'] = ''
            if not 'usage' in kwargs: kwargs['usage'] = ''
            if not 'logo' in kwargs: kwargs['logo'] = ''
            if not 'url' in kwargs: kwargs['url'] = ''
            self.editTopArea(siteid=kwargs['siteid'],
                             name=kwargs['name'],
                             tier=kwargs['tier'],
                             country=kwargs['country'],
                             usage=kwargs['usage'],
                             url=kwargs['url'],
                             logo=kwargs['logo'])
        elif kwargs['region'] == 'config':
            if not 'ce' in kwargs: kwargs['ce'] = ''
            if not 'se' in kwargs: kwargs['se'] = ''
            if not 'gocdbid' in kwargs: kwargs['gocdbid'] = ''
            if not 'manual' in kwargs: kwargs['manual'] = ''
            if not 'devel' in kwargs: kwargs['devel'] = ''
            if not 'phedex' in kwargs: kwargs['phedex'] = ''
            self.editConfig(siteid = kwargs['siteid'],
                            ce = kwargs['ce'],
                            se = kwargs['se'],
                            gocdbid = kwargs['gocdbid'],
                            manual = kwargs['manual'],
                            devel = kwargs['devel'],
                            phedex = kwargs['phedex'])
        elif kwargs['region'] == 'editperson':
            self.editPerson(kwargs)
        elif kwargs['region'] == 'editpersongroup':
            self.editPersonGroup(kwargs)
        elif kwargs['region'] == 'addperson':
            self.addPerson(kwargs)
        elif kwargs['region'] == 'deleteperson':
            self.deletePerson(kwargs)
        elif kwargs['region'] == 'addsite':
            self.addSite(kwargs)
        elif kwargs['region'] == 'delsite':
            self.deleteSite(kwargs)
        elif kwargs['region'] == 'installs':
            self.pinSoftware(kwargs)
        else:
            #TODO: Throw exception here
            return '''I'm sorry, Dave, I can't do that... %s''' % kwargs['region']
    index.exposed = True
    
class RolesAndGroups(SiteDB):
    @is_authenticated (onFail=NotAuthenticated)
    def index(self):
        return self.templatePage ("RolesAndGroups_index",{'token': SecurityToken()}) 
    index.exposed = True
    
    @is_authorized (Role("Global Admin"), Group("global"), 
                    onFail=RedirectToLocalPage("/sitelist/"))    
    def addRole(self, *args, **kwargs):
        return self.templatePage ("RolesAndGroups_add",{"type":"role"}) 
    addRole.exposed = True
   
    @is_authorized (Role("Global Admin"), Group("global"), 
                    onFail=RedirectToLocalPage("/sitelist/"))
    def addGroup(self):
        return self.templatePage ("RolesAndGroups_add",{"type":"group"}) 
    addGroup.exposed = True
    
    @is_authorized (Role("Global Admin"), Group("global"), 
                    onFail=RedirectToLocalPage("/sitelist/"))    
    def deleteRole(self):
        fields = ['title']
        select = "select title from role"
        roles = self.db.getDataObject(fields, select, {})

        return self.templatePage ("RolesAndGroups_delete",{"type":"role", "list": roles}) 
    deleteRole.exposed = True
    
    @is_authorized (Role("Global Admin"), Group("global"), 
                    onFail=RedirectToLocalPage("/sitelist/"))
    def deleteGroup(self):
        fields = ['title']
        select = "select name from user_group"
        groups = self.db.getDataObject(fields, select, {})

        return self.templatePage ("RolesAndGroups_delete",{"type":"group", "list": groups}) 
    deleteGroup.exposed = True
    
    @is_authorized (Role("Global Admin"), Group("global"), 
                    onFail=RedirectToLocalPage("/sitelist/"))
    def edit(self, *args, **kwargs):
        sql = ""
        if kwargs['task'] == "add":
            sql = "insert into table (col) values(:name)"
        elif kwargs['task'] == "delete":
            sql = "delete from table where col = :name" 
        else:
            raise HTTPRedirect(self.baseurl + '/sitelist/')
        col = "title"
        if not kwargs['type']:
            raise HTTPRedirect(self.baseurl + '/sitelist/')
        elif kwargs['type'] == "group":
            kwargs['type'] = "user_group"
            col = "name"

        binds = {'name': kwargs['name']}    
        sql = sql.replace('table', kwargs['type'])
        if self.db.connectionType () == 'oracle' or self.db.connectionType () == 'SQLAlchemy' and kwargs['task'] == "add":
            col = col + ", id"
            sql = sql.replace(':name', ':name, %s_sq.nextval' % kwargs['type'])
        sql = sql.replace('col', col)
        self.db.editDataObject(sql, binds)
        raise HTTPRedirect(self.baseurl + '/rolesandgroups/')
    edit.exposed = True
    
    def showgroup(self, *args, **kwargs):
        """
        Show the members of a group and the roles they posess.
        """
        return self.templatePage ("RolesAndGroups_showgroup",{'token': SecurityToken(), 'group': args[0]}) 
    showgroup.exposed = True
      
class Survey(SiteDB):    
    def createsurvey(self, *args, **kwargs):
        survey = SiteSurvey(self.context)
        start = time.mktime(datetime.datetime.now().timetuple())
        secmod = self.context.SecurityDBApi()
        if len(args) == 0 and len(kwargs) == 0:
            return self.templatePage ("Surveys_create", {'survey':survey, 
                                                     'timestamp':start,
                                                     'tiers':self.db.getTierList(),
                                                     'siteroles':self.db.getSiteRoleList(),
                                                     #'groups':self.db.getGroupList(),
                                                     #'grouproles':self.db.getGroupRoleList(),
                                                     'warning':'None',
                                                     'kwargs':'None'
                                                     })
        else:
            if 'duration' in kwargs and 'startdate' in kwargs and 'sitewho' in kwargs and 'name' in kwargs and kwargs['duration'] != 'None':
            #if ('duration', 'startdate', 'sitewho', 'groupwho', 'name') in kwargs and kwargs['duration'] != 'None':    
                id = survey.newSurvey(kwargs['duration'], 
                                 kwargs['startdate'], 
                                 kwargs['name'], 
                                 secmod.getIDFromUsername(SecurityToken().dn), 
                                 kwargs['sitewho'])
                #, kwargs['groupwho']) #need to add a survey_group table
                return self.templatePage ("Surveys_addQuestion",{'id': id,
                                                                 'warning': 'None',
                                                                 'name': kwargs['name'],
                                                                 'survey': survey})
            elif 'action' in kwargs:
                if kwargs['action'] == "Add another question":
                    survey.newQuestion(kwargs['id'], kwargs['question'], kwargs['response_type'])
                    return self.templatePage ("Surveys_addQuestion",{'id': kwargs['id'],
                                                                 'warning': 'None',
                                                                 'name': kwargs['name'],
                                                                 'survey': survey})
                elif kwargs['action'] == 'Submit Survey':
                    self.context.Logger().message('Survey complete')
                    survey.newQuestion(kwargs['id'], kwargs['question'], kwargs['response_type'])
                    return self.templatePage ("Surveys_submit",{'id': kwargs['id'],
                                                                 'warning': 'None',
                                                                 'name': kwargs['name'],
                                                                 'survey': survey})
            else:
                return self.templatePage ("Surveys_create", {'survey':survey, 
                                                     'timestamp':start,
                                                     'tiers':self.db.getTierList(),
                                                     'siteroles':self.db.getSiteRoleList(),
                                                     #'groups':self.db.getGroupList(),
                                                     #'grouproles':self.db.getGroupRoleList(),
                                                     'warning':'Please fill in all fields',
                                                     'kwargs':kwargs
                                                     })
                    
    createsurvey.exposed = True    

    def completesurvey(self, *args, **kwargs):
        survey = SiteSurvey(self.context)
        secmod = self.context.SecurityDBApi()
        id = 0
        if 'surveyid' in kwargs:
            id = int(kwargs['surveyid'])
        if 'action' in kwargs:
            select = "select tier.name, site.name from site join tier on tier.id = site.tier"
            tierlist = self.db.getDataObject(['tier', 'name'], select)
            tierdict = {}
            for t in tierlist:
                tierdict[tierlist[t]['name']] = tierlist[t]['tier']
            if kwargs['action'] == 'answer':
                kwargs.pop('action')
                kwargs.pop('surveyid')
                role = survey.getFullSurveyList()[id]['wholist'][0][0]
                siteresplist = secmod.sitesForRole(SecurityToken().dn, role)
                for a in kwargs:
                    if survey.getFullSurveyList()[id]['wholist'][0][1] == "All Tiers":
                        for s in siteresplist:
                            survey.addAnswer(siteresplist[s]['id'],
                                             a, kwargs[a],
                                             secmod.getIDFromUsername(SecurityToken().dn))
                    else:
                        for s in siteresplist:
                            if tierdict[siteresplist[s]['sites']] == survey.getFullSurveyList()[id]['wholist'][0][1]:
                                survey.addAnswer(siteresplist[s]['id'],
                                             a, kwargs[a],
                                             secmod.getIDFromUsername(SecurityToken().dn))
                return self.templatePage ("Surveys_complete", {'showlist':True,
                                                           'survey':survey,
                                                           'tierlist':tierdict,
                                                           'warning':'Thank you for answering the survey!',
                                                           'token':SecurityToken()})       

            select = "select tier.name, site.name from site join tier on tier.id = site.tier"
            tierlist = self.db.getDataObject(['tier', 'name'], select)
            tierdict = {}
            for t in tierlist:
                tierdict[tierlist[t]['name']] = tierlist[t]['tier']
            return self.templatePage ("Surveys_complete", {'showlist':True,
                                                           'survey':survey,
                                                           'tierlist':tierdict,
                                                           'warning':'Thank you for answering the survey!',
                                                           'token':SecurityToken()})
                                
        elif id > 0 and secmod.hasRole(SecurityToken().dn, 
                           survey.getFullSurveyList()[id]['wholist'][0][0]):
            return self.templatePage ("Surveys_complete", {'showlist':False,
                                                           'surveyid':id,
                                                           'warning':'None',
                                                           'timestamp':time.mktime(datetime.datetime.now().timetuple()),
                                                           'survey':survey})
        else:
            select = "select tier.name, site.name from site join tier on tier.id = site.tier"
            tierlist = self.db.getDataObject(['tier', 'name'], select)
            tierdict = {}
            for t in tierlist:
                tierdict[tierlist[t]['name']] = tierlist[t]['tier']
            return self.templatePage ("Surveys_complete", {'showlist':True,
                                                           'survey':survey,
                                                           'tierlist':tierdict,
                                                           'warning':'None',
                                                           'token':SecurityToken()})
    completesurvey.exposed = True
    
    def viewresults(self, *args, **kwargs):
        survey = SiteSurvey(self.context)
        id = 0
        if 'id' in kwargs:
            id = int(kwargs['id'])
           
        return self.templatePage ("Surveys_view", {'id':id,
                                                   'survey':survey})
    viewresults.exposed = True
    
    def index(self):
        survey = SiteSurvey(self.context)
        return self.templatePage ("Surveys_index", {'survey':survey})  
    index.exposed = True

class EmailInterface(object):
    def init(self, *args):
        self.smtp = ''
        self.emailer = '' # Some email sending component
    
    def getEmail(self, contacts):
        """
        Get the email address for all people in the contacts list 
        """
        emails = ''
        if not isinstance(contacts, list):
            contacts = [contacts]
        
    
    def sendMessage(self, *args):
        message = self.emailer.newmessage()
        message.to = getEmail(args['contacts'])

class WebAPI(object):
    methods = {}
    @is_authenticated (onFail=siteDBNotAuthenticated)
    def auth_return(self, type=None):
        return self.templatePage ("API_index",{'methods':self.methods, 'type':type})
    
    def dnUserName(self, dn = None):
        hn = self.context.SecurityDBApi().getUsernameFromDN(dn)
        return {'dn': dn, 'user':hn.values()[0]['username']}
    
    def getResponsibility(self, sql='', binds = {}):
        "run sql with binds and return a list of pairs."
        dict={}
        if sql!='' and binds != {}:
            dict = self.db.getDataObject(['role', 'name'], sql, binds)
        else:
            dict = {'Error':'No sql/bind information'}
        return dict
    
    def getSiteResponsibility(self, hn=None, dn=None):
        "Return role:site pairs"
        sqlsel = ''
        binds = {}
        if hn:
            sqlsel = "(select id from contact where username = :hn)"
            binds = {'hn':hn}
        elif dn:
            sqlsel = "(select id from contact where dn = :dn)"
            binds = {'dn':dn} 
        sql = """select role.title, site.name from SITE_RESPONSIBILITY
join contact on contact.id = SITE_RESPONSIBILITY.contact
join ROLE on role.ID = SITE_RESPONSIBILITY.role
join site on site.id = SITE_RESPONSIBILITY.site
 where SITE_RESPONSIBILITY.contact = %s""" % sqlsel
        return self.getResponsibility(sql,binds)
    
    def getGroupResponsibility(self, hn=None, dn=None):
        "Return role:group pairs"
        sql = ''
        binds = {}
        if hn:
            sqlsel = "(select id from contact where username = :hn)"
            binds = {'hn':hn}
        elif dn:
            sqlsel = "(select id from contact where dn = :dn)"
            binds = {'dn':dn} 
        sql = """select role.title, USER_GROUP.name from GROUP_RESPONSIBILITY
join contact on contact.id = GROUP_RESPONSIBILITY.contact
join ROLE on role.ID = GROUP_RESPONSIBILITY.role
join USER_GROUP on user_group.id = GROUP_RESPONSIBILITY.USER_GROUP
 where GROUP_RESPONSIBILITY.contact = %s""" % sqlsel
 
        return self.getResponsibility(sql,binds)
 
    def sitenames(self, *args, **kwargs):
        cmssitelist = {}
        plist = {}
        celist = {}
        selist = {}
        sql = ""
        if 'site' not in kwargs.keys() or kwargs['site'] == '':
            binds = None
            sql = """select site.name as SiteName, cms_name.name as CMSName, sam_name.name as SAMName, CE.fqdn as CE_fqdn, SE.fqdn as SE_fqdn, phedex_node.name as PhEDEXNode from site

join (
    select resource_element.site as site, RESOURCE_ELEMENT.fqdn as fqdn from RESOURCE_ELEMENT where TYPE='CE'
) CE on site.id = CE.site

join (
    select resource_element.site as site, RESOURCE_ELEMENT.fqdn as fqdn from RESOURCE_ELEMENT where TYPE='SE'
) SE on site.id = SE.site

join SITE_CMS_NAME_MAP on SITE_CMS_NAME_MAP.SITE_ID = site.id
join cms_name on cms_name.ID = SITE_CMS_NAME_MAP.CMS_NAME_ID
join SAM_CMS_NAME_MAP on SAM_CMS_NAME_MAP.CMS_NAME_ID = cms_name.ID
join sam_name on sam_name.ID = SAM_CMS_NAME_MAP.SAM_ID

join phedex_node on phedex_node.site = site.id

order by site.tier, site.name"""
        else:
            sql = """select site.name as SiteName, cms_name.name as CMSName, sam_name.name as SAMName, CE.fqdn as CE_fqdn, SE.fqdn as SE_fqdn, phedex_node.name as PhEDEXNode from site

join (
    select resource_element.site as site, RESOURCE_ELEMENT.fqdn as fqdn from RESOURCE_ELEMENT where TYPE='CE'
) CE on site.id = CE.site

join (
    select resource_element.site as site, RESOURCE_ELEMENT.fqdn as fqdn from RESOURCE_ELEMENT where TYPE='SE'
) SE on site.id = SE.site

join SITE_CMS_NAME_MAP on SITE_CMS_NAME_MAP.SITE_ID = site.id
join cms_name on cms_name.ID = SITE_CMS_NAME_MAP.CMS_NAME_ID
join SAM_CMS_NAME_MAP on SAM_CMS_NAME_MAP.CMS_NAME_ID = cms_name.ID
join sam_name on sam_name.ID = SAM_CMS_NAME_MAP.SAM_ID

join phedex_node on phedex_node.site = site.id

where site.name = :site_name
order by site.tier"""
            binds = {'site_name':kwargs['site']}

        dict = self.db.getDataObject(['site', 'ce', 'se', 'p_node'], sql, binds)
        if 'type' not in kwargs.keys() or kwargs['type'] == 'cmssitelist':
           # for d in dict:
            #    cmssitelist[d['site']] = {'celist':[], 'selist':[], 'p_list':[]}
            for i in dict:
                d = dict[i]
                if d['site'] in cmssitelist.keys():
                    if d['p_node'] not in cmssitelist[d['site']]['p_list']:
                        cmssitelist[d['site']]['p_list'].append(d['p_node'])
                    if d['se'] not in cmssitelist[d['site']]['selist']:
                        cmssitelist[d['site']]['selist'].append(d['se'])
                    if d['ce'] not in cmssitelist[d['site']]['celist']:
                        cmssitelist[d['site']]['celist'].append(d['ce'])
                else:
                    cmssitelist[d['site']] = {'p_list':[d['p_node']], 'selist':[d['se']], 'celist':[d['ce']]}

        elif kwargs['type'] =='phedexlist':
            for i in dict:
                d = dict[i]
                if d['p_node'] in plist.keys():
                    if d['se'] not in plist[d['p_node']]['selist']:
                        plist[d['p_node']]['selist'].append(d['se'])
                    if d['ce'] not in plist[d['p_node']]['celist']:
                        plist[d['p_node']]['selist'].append(d['se'])
                    if d['site'] not in plist[d['p_node']]['cmslist']:
                        plist[d['p_node']]['cmslist'].append(d['site'])
                else:
                    plist[d['p_node']] = {'selist':[d['se']], 'cmslist':[d['site']], 'celist':[d['ce']]}

        elif kwargs['type'] == 'celist':
            for i in dict:
                d = dict[i]
                if d['ce'] in celist.keys():
                    if d['p_node'] not in celist[d['ce']]['p_list']:
                        celist[d['ce']]['p_list'].append(d['p_node'])
                    if d['se'] not in celist[d['ce']]['selist']:
                        celist[d['ce']]['selist'].append(d['se'])
                    if d['site'] not in celist[d['ce']]['cmslist']:
                        celist[d['ce']]['cmslist'].append(d['site'])
                else:
                    celist[d['ce']] = {'p_list':[d['p_node']], 'selist':[d['se']], 'cmslist':[d['site']]}

        elif kwargs['type'] == 'selist':
            for i in dict:
                d = dict[i]
                if d['se'] in selist.keys():
                    if d['p_node'] not in selist[d['se']]['p_list']:
                        selist[d['se']]['p_list'].append(d['p_node'])
                    if d['ce'] not in selist[d['se']]['celist']:
                        selist[d['se']]['celist'].append(d['ce'])
                    if d['site'] not in selist[d['se']]['cmslist']:
                        selist[d['se']]['cmslist'].append(d['site'])
                else:
                    selist[d['se']] = {'p_list':[d['p_node']], 'cmslist':[d['site']], 'celist':[d['ce']]}
        {'cmssitelist':cmssitelist}
    
    def CMStoSiteName(self,name):
        sql = """select site.name from cms_name 
            join SITE_CMS_NAME_MAP on SITE_CMS_NAME_MAP.CMS_NAME_ID = cms_name.ID
            join site on site.id = SITE_CMS_NAME_MAP.SITE_ID
            where cms_name.name like :sitename"""
        binds = {'sitename': name+"%"}
        dict = self.db.getDataObject(['name'], sql, binds)
        return dict

    def SitetoCMSName(self,name):
        sql = """select cms_name.name from site
            join SITE_CMS_NAME_MAP on SITE_CMS_NAME_MAP.SITE_ID = site.id
            join cms_name on cms_name.id = SITE_CMS_NAME_MAP.CMS_NAME_ID            
            where site.name like :sitename"""
        binds = {'sitename': name+"%"}
        dict = self.db.getDataObject(['name'], sql, binds)
        return dict
               
    def PhEDExNodetoCMSName(self,node_name):
        #TODO: Needs to be improved for compound sites
        sql = """select cms_name.name from phedex_node 
            join phedex_node_cms_name_map on phedex_node_cms_name_map.node_id = phedex_node.id 
            join CMS_NAME on CMS_NAME.id = phedex_node_cms_name_map.cms_name_id
            where phedex_node.name = :nodename"""
        binds = {'nodename': node_name+"%"}
        dict = self.db.getDataObject(['cms_name'], sql, binds)
        return dict   
    
    def CMSNametoPhEDExNode(self,cms_name):
        #TODO: Needs to be improved for compound sites
        sql = """select phedex_node.name from phedex_node 
            join phedex_node_cms_name_map on phedex_node_cms_name_map.node_id = phedex_node.id 
            join CMS_NAME on CMS_NAME.id = phedex_node_cms_name_map.cms_name_id
            where cms_name.name like :cmsname"""
        binds = {'cmsname': cms_name+"%"}
        dict = self.db.getDataObject(['phedex_node'], sql, binds)
        return dict   
      
    def CMStoSAMName(self,name):
        sql = """select SAM_NAME.name from cms_name
            join SAM_CMS_NAME_MAP on SAM_CMS_NAME_MAP.CMS_NAME_ID = cms_name.id
            join SAM_NAME on SAM_NAME.id = SAM_CMS_NAME_MAP.SAM_ID
            where cms_name.name like :sitename"""
        binds = {'sitename': name+"%"}
        dict = self.db.getDataObject(['name'], sql, binds)
        return dict
    
    def SAMtoCMSName(self,name):
        sql = """select cms_name.name from SAM_NAME
            join SAM_CMS_NAME_MAP on SAM_CMS_NAME_MAP.SAM_ID = SAM_NAME.id
            join cms_name on cms_name.id = SAM_CMS_NAME_MAP.CMS_NAME_ID
            where SAM_NAME.name like :sitename"""
        binds = {'sitename': name+"%"}
        dict = self.db.getDataObject(['name'], sql, binds)
        return dict
            
    def SitetoSAMName(self,name):
        sql = """select SAM_NAME.name from site
            join SITE_CMS_NAME_MAP on SITE_CMS_NAME_MAP.SITE_ID = site.ID
            join SAM_CMS_NAME_MAP on SAM_CMS_NAME_MAP.CMS_NAME_ID = SITE_CMS_NAME_MAP.CMS_NAME_ID
            join SAM_NAME on SAM_NAME.ID = SAM_CMS_NAME_MAP.SAM_ID
            where site.name like :sitename"""
        binds = {'sitename': name+"%"}
        dict = self.db.getDataObject(['name'], sql, binds)
        return dict
    
    def SAMtoSiteName(self,name):
        sql = """select site.name from SAM_NAME
            join SAM_CMS_NAME_MAP on SAM_CMS_NAME_MAP.SAM_ID = SAM_NAME.id
            join SITE_CMS_NAME_MAP on SITE_CMS_NAME_MAP.CMS_NAME_ID = SAM_CMS_NAME_MAP.CMS_NAME_ID
            join site on site.ID = SITE_CMS_NAME_MAP.SITE_ID
            where SAM_NAME.name like :sitename"""
        binds = {'sitename': name+"%"}
        dict = self.db.getDataObject(['name'], sql, binds)
        return dict

    def SEtoCMSName(self,name, restype='SE'):
        sql = """select CMS_NAME.name from resource_element
            join resource_CMS_NAME_MAP on resource_CMS_NAME_MAP.resource_ID = resource_element.id
            join CMS_NAME on CMS_NAME.id = resource_CMS_NAME_MAP.CMS_NAME_ID
            where resource_element.fqdn like :sename
            and resource_element.type = :restype"""
        binds = {'sename': name+"%", 'restype':restype}
        dict = self.db.getDataObject(['name'], sql, binds)
        return dict
    
    def CMSNametoSE(self,name, restype='SE'):
        sql = """select resource_element.fqdn from CMS_NAME
            join resource_CMS_NAME_MAP on resource_CMS_NAME_MAP.CMS_NAME_ID = CMS_NAME.id
            join resource_element on resource_element.id = resource_CMS_NAME_MAP.resource_ID
            where CMS_NAME.name like :sitename
            and resource_element.type = :restype"""
        binds = {'sitename': name+"%", 'restype':restype}
        dict = self.db.getDataObject(['name'], sql, binds)
        return dict
    
    def CEtoCMSName(self,name):
        return self.SEtoCMSName(name, 'CE')
    
    def SquidtoCMSName(self,name):
        return self.SEtoCMSName(name,'SQUID')
    
    def CMSNametoCE(self,name):
        return self.CMSNametoSE(name, 'CE')
    
    def CMSNametoSquid(self,name):
        return self.CMSNametoSE(name, 'SQUID')
    
    def CMSNametoAdmins(self, name, role = None):
        sql = """select contact.forename, contact.surname, contact.email, role.title
from CMS_NAME
join SITE_CMS_NAME_MAP on SITE_CMS_NAME_MAP.CMS_NAME_ID = cms_name.ID
join site_responsibility on site_responsibility.site = SITE_CMS_NAME_MAP.SITE_ID
join contact on contact.id = site_responsibility.contact
join role on role.id = site_responsibility.role
where CMS_NAME.name like :sitename
"""
        binds = {'sitename': name+"%"}
        if role != None:
            sql = "%s and site_responsibility.role = (select id from role where title like :roletitle)" % sql
            binds['roletitle'] = role
        dict = self.db.getDataObject(['forename', 'surname', 'email', 'title'], sql, binds)
        return dict   
    
    def PeopleWithRoleInGroup(self, role = None, group = None):
        for i in (role, group):
            if i != None:
                i = urllib.unquote(i)
        """
        Return all the people with a certain role in a group
        """
        sql = """select contact.forename, contact.surname, contact.email, contact.DN, contact.username from 
        GROUP_RESPONSIBILITY
        join contact on contact.id = GROUP_RESPONSIBILITY.contact
        where GROUP_RESPONSIBILITY.USER_GROUP = (select id from user_group where name=:group)
        and GROUP_RESPONSIBILITY.role= (select id from role where title=:role)
        """
        binds = {'role':role, 'group': group}
        dict = self.db.getDataObject(['forename', 'surname', 'email', 'DN', 'username'], sql, binds)
        return dict
    
    def SiteStatus(self, cms_name = None):
        "Return the status of the site: up/warning/down/maintenance"
        dict = {}
        if cms_name:
            if type(cms_name) == type("string"):
                cms_name = [cms_name]
        
        else:
            dict = {'Error':'No cms_name given'}
        for s in cms_name:
            try:
                resources = {}
                if re.compile("[0-9]+").match(s):
                    sql = """select resource_element.fqdn, site_cms_name_map.site_id from CMS_NAME
                        join resource_CMS_NAME_MAP on resource_CMS_NAME_MAP.CMS_NAME_ID = CMS_NAME.id
                        join resource_element on resource_element.id = resource_CMS_NAME_MAP.resource_ID
                        join site_cms_name_map on site_cms_name_map.CMS_NAME_ID = CMS_NAME.id
                        where site_cms_name_map.site_id = :siteid
                        and resource_element.type in ('SE','CE')"""
                    binds = {'siteid': s}
                    resources = self.db.getDataObject(['name', 'siteid'], sql, binds)
                if re.compile("T[0-9]_[A-Z,a-z]+_*").match(s):
                    sql = """select resource_element.fqdn, site_cms_name_map.site_id from CMS_NAME
                        join resource_CMS_NAME_MAP on resource_CMS_NAME_MAP.CMS_NAME_ID = CMS_NAME.id
                        join resource_element on resource_element.id = resource_CMS_NAME_MAP.resource_ID
                        join site_cms_name_map on site_cms_name_map.CMS_NAME_ID = CMS_NAME.id
                        where CMS_NAME.name like :sitename
                        and resource_element.type in ('SE','CE')"""
                    binds = {'sitename': s}
                    resources = self.db.getDataObject(['name', 'siteid'], sql, binds)
                if resources != {}:
                    path = __file__.rsplit('/',1)[0]
                    summaryfile = "%s/csv/db_sam_summary_%s.csv" % (path, s)
                    t = datetime.datetime.now() - datetime.timedelta(hours=0.5)
                    if not os.path.exists(summaryfile) or os.path.getmtime(summaryfile) < time.mktime(t.timetuple()):
                        if len(resources) > 0:
                            u = urllib.URLopener()
                            u.addheader('Accept', 'text/csv')
                            url = self.context.ConfigParser().get("endpoint", "dashboard")
                            url = '%s/latestresults' % url
                            for r in resources:
                                if resources.keys().index(r) == 0:
                                    url = '%s?service=%s' % (url, resources[r]['name'])
                                else:
                                    url = '%s&service=%s' % (url, resources[r]['name']) 
                            self.context.Logger().warning("Downloading xml summary file - %s: %s" % (summaryfile, url))
                            results = u.retrieve(url, summaryfile)
                    f=open(summaryfile, 'r')
                    status = []
                    for l in f.readlines():
                        status.append(l.strip().rsplit(',',1)[1])
                        self.context.Logger().message(status)
                    for i in ["MAINTENANCE", "ERROR", "WARNING", "UP"]:
                        if i in status and s not in dict.keys():
                             dict[s] = {'status':i, 'id':resources[0]['siteid']}
                else:
                     dict[s] = "WARNING"
            except Exception, e:
                self.context.Logger().error(e)
                dict[s] = {'status':"UNKNOWN", 'id':0}
        return dict
    
    def Pledge(self, site = None):
      from datetime import date
      if site != None:
        if not site.isdigit():
            #site is the site name, not the id
            fields = {}
            fields['siteid'] = ['id', 'name']
            select = """select id, name from site
            join SITE_CMS_NAME_MAP on SITE_CMS_NAME_MAP.SITE_ID = site.id
            join cms_name on cms_name.id = SITE_CMS_NAME_MAP.CMS_NAME_ID            
            where cms_name.name like :site"""
            binds = { 'site' : site }
            data = self.db.getDataObject(fields['siteid'], select, binds)
            site = {}
            if len(data) > 0:
                site = data[0]['id']
      now = date.today()
      year = now.year
      quarter = 0
      for i in xrange(0, 4, 1):
        if now.month in xrange ((3*i) + 1, 1 + (3*(1+i)), 1):
          quarter = i + 1
        
      resources = SiteResources(self.context, site)
      if site == None:
          site = "global"
      resources.publicResources(quarter, year)
      return {0: resources.pledge}

    def Groups(self):
        """
        Available groups in SiteDB
        """
        sql = "select ID, NAME from USER_GROUP"
        dict = self.db.getDataObject(['id', 'name'], sql)
        return dict
    
    def RolesForGroup(self, group = None):
        """
        Roles a member of a group can have
        """
        dict = {}
        if group == 'site':
            sql = "select id, title from ROLE where id in (select distinct role from SITE_RESPONSIBILITY)"
            dict = self.db.getDataObject(['id', 'title'], sql)
        else:
            sql = "select id, title from ROLE where id in (select DISTINCT role from group_responsibility where user_group=(select id from user_group where name=:group))"
            binds = {'group': group}
            dict = self.db.getDataObject(['id', 'title'], sql, binds)
        return dict

    def __init__(self):
        self.methods = {'sitenames':{'args':['cmssitelist', 
                                 'phedexlist', 'celist', 
                                 'selist'],'call':self.sitenames},
                           'dnUserName':{'args':['dn'],'call':self.dnUserName},
                           'getSiteResponsibility':{'args':['hn','dn'], 'call':self.getSiteResponsibility},
                           'getGroupResponsibility':{'args':['hn','dn'], 'call':self.getGroupResponsibility},
                           'SitetoCMSName':{'args':['name'],'call':self.SitetoCMSName},
                           'CMStoSiteName':{'args':['name'],'call':self.CMStoSiteName},
                           'CMStoSAMName':{'args':['name'], 'call':self.CMStoSAMName},
                           'SAMtoCMSName':{'args':['name'],'call':self.SAMtoCMSName},
                           'SEtoCMSName':{'args':['name'],'call':self.SEtoCMSName},
                           'CMSNametoSE':{'args':['name'],'call':self.CMSNametoSE},
                           'CEtoCMSName':{'args':['name'],'call':self.CEtoCMSName},
                           'CMSNametoCE':{'args':['name'],'call':self.CMSNametoCE},
                           'SitetoSAMName':{'args':['name'],'call':self.SitetoSAMName},
                           'SAMtoSiteName':{'args':['name'],'call':self.SAMtoSiteName},
                           'CMSNametoAdmins':{'args':['name', 'role'],'call':self.CMSNametoAdmins},
                           'SiteStatus':{'args':['cms_name'],'call':self.SiteStatus},
                           'PhEDExNodetoCMSName':{'args':['node_name'],'call':self.PhEDExNodetoCMSName},
                           'CMSNametoPhEDExNode':{'args':['cms_name'],'call':self.CMSNametoPhEDExNode},
                           'Pledge':{'args':['site'],'call':self.Pledge},
                           'Groups':{'args':[],'call':self.Groups},
                           'RolesForGroup':{'args':['group'],'call':self.RolesForGroup},
                           'PeopleWithRoleInGroup':{'args':['group','role'],'call':self.PeopleWithRoleInGroup},
                    }

class XML(SiteDB, WebAPI):
     
    def index(self, *args, **kw):
        WebAPI.__init__ (self)
        if len(args) == 0:
            return self.auth_return(type='XML')
        else:
            import cherrypy
            cherrypy.response.headers['Content-Type'] = "application/xhtml+xml"
            kwargs=''
            for i in kw:
                kwargs = kwargs + "%s='%s'" % (i, kw[i])
            str = "self.methods[args[0]]['call'](%s)" % kwargs
            dict = {}
            try:
                dict = eval(str)
            except Exception, e:
                error = e.__str__()
                self.context.Logger().debug(error)
                self.context.Logger().debug("%s:%s" % (sys.exc_type, sys.exc_value))
                dict = {0:{'Exception_thrown_in':args[0],
                           'Exception_type': '%s' % sys.exc_type,
                           'Exception_detail':error, 
                           'Exception_string':str, 
                           'Exception_dict':dict}}
            
            self.context.Logger().debug(str)
            self.context.Logger().debug(dict)
            return self.templatePage ("XML_Results", {'results':dict})
    index.exposed = True
    
class JSON(SiteDB, WebAPI):
    "The JSON API for SiteDB"
    from Tools.JSONSerializer import PythonDictSerializer as PythonDictSerializerJSON
    json = PythonDictSerializerJSON()
     
    def index(self, *args, **kw):
        WebAPI.__init__ (self)
        if len(args) == 0:
            return self.auth_return(type='JSON')
        else:
            kwargs=''
            for i in kw:
                kwargs = kwargs + "%s='%s'," % (i, kw[i])
            str = "self.methods[args[0]]['call'](%s)" % kwargs.strip(',')
            dict = {}
            try:
                dict = eval(str)
            except Exception, e:
                error = e.__str__()
                self.context.Logger().debug(error)
                self.context.Logger().debug("%s:%s" % (sys.exc_type, sys.exc_value))
                dict = {0:{'Exception_thrown_in':args[0],
                           'Exception_type': '%s' % sys.exc_type,
                           'Exception_detail':error, 
                           'Exception_string':str, 
                           'Exception_dict':dict}}
            
            self.context.Logger().debug(str)
            self.context.Logger().debug(dict)
            return self.json(dict)
    index.exposed = True        

class SiteDBRoot(Controller):
    def __init__ (self, context):
        Controller.__init__ (self, context, __file__)
        self.basepath = __file__.rsplit('/', 1)[0]
        context.OptionParser().add_option ("--my-sitedb-ini",
                                        help = "Path to the siteDB ini file",
                                        default = join (self.basepath, "sitedb.ini"),
                                        dest = "cfgFilename")

DeclarePlugin ("/Controllers/SiteDB/Root", SiteDBRoot, options={"baseUrl": "/common"}) # CSS/JS/images - set in framework
DeclarePlugin ("/Controllers/SiteDB/Hello world", Test, options={"baseUrl": "/HelloWorld"})
DeclarePlugin ("/Controllers/SiteDB/SiteList", SiteList, options={"baseUrl": "/sitelist"})
DeclarePlugin ("/Controllers/SiteDB/Site", Site, options={"baseUrl": "/site"})
DeclarePlugin ("/Controllers/SiteDB/Admin", Admin, options={"baseUrl": "/admin"})
DeclarePlugin ("/Controllers/SiteDB/People", People, options={"baseUrl": "/people"})
DeclarePlugin ("/Controllers/SiteDB/Reports", Reports, options={"baseUrl": "/reports"})
DeclarePlugin ("/Controllers/SiteDB/Resources", Resources, options={"baseUrl": "/resources"})
DeclarePlugin ("/Controllers/SiteDB/EditSite", EditSite, options={"baseUrl": "/editsite"})
DeclarePlugin ("/Controllers/SiteDB/Surveys", Survey, options={"baseUrl": "/surveys"})
DeclarePlugin ("/Controllers/SiteDB/XML", XML, options={"baseUrl": "/xml"})
DeclarePlugin ("/Controllers/SiteDB/JSON", JSON, options={"baseUrl": "/json"})
DeclarePlugin ("/Controllers/SiteDB/RolesAndGroups", RolesAndGroups, options={"baseUrl": "/rolesandgroups"})
#DeclarePlugin ("/Controllers/SiteDB/Test", Test, options={"baseUrl": "/test"})

