"SiteDB API"
from ConfigParser import ConfigParser
from os import getenv
from datetime import date
from datetime import datetime, timedelta
import time, urllib, os
from BeautifulSoup import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy import __version__ as sqlalchemy_version
import sqlalchemy.pool as pool
try:
    from pysqlite2 import dbapi2 as sqlite
except ImportError, e:
    try:
        from sqlite3 import dbapi2 as sqlite #try the 2.5+ stdlib name.
    except ImportError:
        raise e


class SiteDBApi:
  context = ''
  database = ''
  def __init__(self, context):
    self.context = context
    self.dbi = _ConnectionHolder()
    self.dbi.con = ''
    self.dbi.type = ''
    self.connections = []

  def regexp(expr, item):
    r = re.compile(expr)
    return r.match(item) is not None
  
  def connectionType(self):
    return self.dbi.type
#    if str(type(self.dbi.con)).lower().count("sqlite"):
#      return "sqlite"
#    elif str(type(self.dbi.con)).lower().count("oracle"):
#      return "oracle"
#    else:
#      return "SQLAlchemy"
      #raise "Unknown database or database type" 

  def connect  (self):
    self.context.Logger().debug("Using SQLAlchemy v.%s" % sqlalchemy_version)
    filename = __file__.rsplit ("/", 1)[0] + "/security.ini"
    if "SEC_MOD_INI" in os.environ:
        filename = os.environ["SEC_MOD_INI"]
    if not os.path.exists(filename):
      self.context.Logger ().message ("Security configuration file does not exists.\n Creating a dummy default one.")
      defaultCfgParser = ConfigParser ()
      defaultCfgParser.add_section ("database")
      defaultCfgParser.set ("database", "dbname", getenv ("PWD") + "/sitedb_test.db")
      defaultCfgParser.set ("database", "dbtype", "sqlite")
      defaultCfgParser.write (file (filename,"w"))
    parser = ConfigParser ()
    self.context.Logger ().message (filename)
    parser.read (filename)
    database = parser.get ("database", "dbname")
    self.dbi.type = parser.get ("database", "dbtype")
    # if database was read from the file and doesn't had any sqlite:/// prefix we must create it
    if self.dbi.type=='sqlite':
       if not database.count('sqlite:///'):
          database="sqlite:///%s"%database
    try:
      #self.context.Logger().message ("Creating engine for %s" % database)
      if database.count('sqlite:///'):
          self.dbi.con = create_engine(database, convert_unicode=True, encoding='utf-8', pool_size=1, pool_recycle=30)
      else:
          self.dbi.con = create_engine(database, convert_unicode=True, encoding='utf-8', pool_size=100, max_overflow=100, pool_recycle=600)
      #dbpool = pool.manage(engine)
      #self.dbi.con = engine.connect()
    except Exception, e:
      self.context.Logger().message ("Could not connect to database engine")
      self.context.Logger().message (e)       

  def close(self):
    logger = self.context.Logger ()
    logger.debug ("Closing database connection")
    if self.testConnection () == True:
      self.dbi.con.dispose()
    logger.message ("Database connection closed")

  def testConnection(self):
    try:
      if self.dbi.con == None: return False
      if self.dbi.con == '': return False
      if self.connectionType() == "sqlite":
        return self.testSqliteConnection()
      elif self.connectionType() == "oracle":
        return self.testOracleConnection()
      else:
        self.context.Logger().message("Unknown database type")
        return False
    except:
      return False
    
  def testOracleConnection( self ):
    try:
      test = 'select * from dual'
      #curs = self.dbi.con.cursor()
      #curs.prepare( test )
      result = self.dbi.con.connect().execute( test )
      
      assert result > 0
      
    except:
      return False
    return True
  
  def testSqliteConnection( self ):
    try:
      test = 'select * from sqlite_master'
      curs = self.dbi.con.cursor()
      curs.execute( test )
      assert len(curs.fetchone()) > 0
      curs.close()
    except Exception, inst:
      return False
    return True

  def getDataObject(self, fieldnames, sqlstmt, binds = None):
    self.context.Logger().message(self.dbi.con.pool.status())
    #connectionType = self.connectionType ()
    conn = self.dbi.con.connect()
    result = ''
#    if connectionType == "oracle" and self.testConnection () == False:
#      self.connectOracle(self.database)
#      cur = self.dbi.con
#      if self.testConnection () == False:
#        self.context.Logger().message("Could not create database connection")
#        raise "hell"
#    else:
#        cur = self.dbi.con.cursor();
#    if connectionType == 'sqlite':
#        print type(conn)
#        print type(conn.connection)
#        conn.connection.create_function("regexp", 2, self.regexp)
    if binds == None:
      try:
        result = conn.execute(sqlstmt)
      except Exception, e:
        self.context.Logger().error(e)
        self.context.Logger().error(sqlstmt)
        raise e
    else:
      try:
        result = conn.execute(sqlstmt, binds)
      except Exception, e:
        self.context.Logger().error(e)
        self.context.Logger().error(sqlstmt)
        self.context.Logger().error(binds)
        raise e
    i = 0
    dataObj = {}
  
    for row in result:
      j = 0
      dataObj[i] = {}
      if type(fieldnames) == type('str'):
        dataObj[i][fieldnames] = row[j]
      else:
        for f in fieldnames:
          dataObj[i][f] = row[j]
          j += 1
      i += 1
    
    conn.close()
    self.context.Logger().message(self.dbi.con.pool.status())
    
    return dataObj

  def editDataObject(self, sqlstmt, binds = None):
    "Can take either a single statement or a list of staments and binds"
    self.context.Logger().message(self.dbi.con.pool.status())
    connectionType = self.connectionType()
    if type(sqlstmt) == type("string"):
        try:
          self.dbi.con.connect().execute(sqlstmt, binds)
        except Exception, e:
          self.context.Logger ().warning (sqlstmt)
          self.context.Logger ().warning (binds)
          self.context.Logger ().warning ("Couldn't commit: %s" % e)
          raise e
    elif type(sqlstmt) == type([]) and type(binds) == type([]) and len(binds) == len(sqlstmt):
        connection = self.dbi.con.connect()
        trans = connection.begin()
        try:
            for s in sqlstmt:
                connection.execute(s, binds[sqlstmt.index(s)])
            trans.commit()
        except Exception, e:
            trans.rollback()
            self.context.Logger ().warning (sqlstmt)
            self.context.Logger ().warning (binds)
            self.context.Logger ().warning ("Couldn't commit: %s" % e)
            raise e
    self.context.Logger().message(self.dbi.con.pool.status())

  def dataObjectFields(self, obj):
    if obj[0]:
      return obj[0].keys();
    else:
      return None

  def getSiteListObj(self, naming_scheme = "name"):
    fields = ('id', 'name', 'tier')
    select = ''
    if naming_scheme == "name":
        select = '''select site.id, site.name, tier.name
  from site join tier on tier.id = site.tier
  order by site.tier, site.name'''
    elif naming_scheme == "cmsname":
        select = '''select site.id, cms_name.name, tier.name from site 
  join tier on tier.id = site.tier
  join site_cms_name_map on site_cms_name_map.site_id = site.id
  join cms_name on cms_name.id = site_cms_name_map.cms_name_id
  order by site.tier, cms_name.name'''
    elif naming_scheme == "lcgname":
        select = '''select site.id, sam_name.name, tier.name from SAM_NAME
  join SAM_CMS_NAME_MAP on SAM_CMS_NAME_MAP.SAM_ID = SAM_NAME.id
  join SITE_CMS_NAME_MAP on SITE_CMS_NAME_MAP.CMS_NAME_ID = SAM_CMS_NAME_MAP.CMS_NAME_ID
  join site on site.ID = SITE_CMS_NAME_MAP.SITE_ID
  join tier on tier.id = site.tier
  order by site.tier, sam_name.name'''
    elif naming_scheme == "phedex":
        select = '''select site.id, phedex_node.name, tier.name from site 
  join tier on tier.id = site.tier
  join phedex_node on phedex_node.site = site.id
  order by site.tier, phedex_node.name'''
    elif naming_scheme == "ce":
        select = '''select site.id, resource_element.fqdn, tier.name from site 
  join tier on tier.id = site.tier
  join resource_element on resource_element.site = site.id
  where resource_element.type = 'CE'
  order by site.tier, resource_element.fqdn'''
    elif naming_scheme == "se":
        select = '''select site.id, resource_element.fqdn, tier.name from site 
  join tier on tier.id = site.tier
  join resource_element on resource_element.site = site.id
  where resource_element.type = 'SE'
  order by site.tier, resource_element.fqdn'''
    data = {}
    try:
      data = self.getDataObject(fields, select)
    except:
      self.context.Logger().message("Could not get SiteList")
      data = {}  
    return data

  def getGroupList(self):
    fields = ('id','name')
    select = 'select id, name from user_group'
    data = {}
    try:
      data = self.getDataObject(fields, select)
    except:
      self.context.Logger().message("Could not get GroupList")
      data = {}
    return data

  def getTierList(self):
    fields = ('id','name')
    select = 'select id, name from tier order by pos'
    data = {}
    try:
      data = self.getDataObject(fields, select)
    except:
      self.context.Logger().message("Could not get TierList")
      data = {}
    return data

  def getSiteRoleList(self):
    #TODO: Restrict to filled site roles only
    fields = ('id','title')
    select = 'select id, title from role where id in (select distinct role from SITE_RESPONSIBILITY) order by title'
    data = {}
    try:
      data = self.getDataObject(fields, select)
    except:
      self.context.Logger().message("Could not get SiteRoleList")
      data = {}
    return data

  def getGroupRoleList(self):
    #TODO: Restrict to filled group roles only
    fields = ('id','title')
    select = 'select id, title from role where id in (select distinct role from GROUP_RESPONSIBILITY) order by title'
    data = {}
    try:
      data = self.getDataObject(fields, select)
    except:
      self.context.Logger().message("Could not get GroupRoleList")
      data = {}
    return data

  def getSitePersonListObj(self, site = None, name = None):
  #Retrives a list of people and their details
  #Given a site ID only people associated with 
  #that site are returned, otherwise it returns 
  #all people in SiteDB.
    fields = ['forename', 'surname', 'email', "phone1", "phone2", "im_handle",
  "role_id", "role_title", "site_name", "site_id", "contact_id"]
    select = """select contact.forename, contact.surname, contact.email, 
 contact.phone1, contact.phone2, contact.im_handle, role.id, role.title,
 site.name, site.id, contact.id
from site_responsibility
join contact on contact.id = site_responsibility.contact
join role on role.id = site_responsibility.role
join site on site.id = site_responsibility.site
 where %s
order by contact.surname"""

    binds = {}
    if site:
      where = 'role.id != 1 and site.id = :site'
      binds = {'site' : site}
    elif name:
      where = """contact.surname = :surname and contact.forename = :forename"""
      binds = {'surname' : name.split()[1], 'forename' : name.split()[0]}
    else:
      where = '1 = 1'

    select = select % where
    data = {}
    try:
      data = self.getDataObject(fields, select, binds)
    except:
      self.context.Logger().message("Could not get SitePersonList")
      data = {}
    return data

  def getGroupPersonListObj(self, group = None, name = None):
  #Retrives a list of people and their details
  #Given a site ID only people associated with 
  #that site are returned, otherwise it returns 
  #all people in SiteDB.
    fields = ['forename', 'surname', 'email', "phone1", "phone2", "im_handle",
  "role_id", "role_title", "group_name", "group_id", "contact_id"]
    select = """select contact.forename, contact.surname, contact.email, 
 contact.phone1, contact.phone2, contact.im_handle, role.id, role.title,
 user_group.name, user_group.id, contact.id
from group_responsibility
join contact on contact.id = group_responsibility.contact
join role on role.id = group_responsibility.role
join user_group on user_group.id = group_responsibility.user_group
 where %s
order by contact.surname"""

    binds = {}
    if group:
      where = 'role.id != 1 and user_group.id = :group'
      binds = {'group' : group}
    elif name:
      where = """contact.surname = :surname and contact.forename = :forename"""
      binds = {'surname' : name.split()[1], 'forename' : name.split()[0]}
    else:
      where = '1 = 1'

    select = select % where
    data = {}
    try:
      data = self.getDataObject(fields, select, binds)
    except:
      self.context.Logger().message("Could not get GroupPersonList")
      data = {}

    return data

  def getSitePersonDict(self, site = None, name = None):
    data = self.getSitePersonListObj(site, name)
    #TODO: Replace roles dict with set
    persondict = {}
    for d in data:
      
      p = data[d]
      
      key = p['surname'] + p['forename'] + p['email']
      if (key in persondict) == False:
        name = p['forename'] + " " + p['surname']
        persondict[key] = {'name':name, 'email':p['email'], 'sites':{}, 'roles':{},
                           'phone1':p['phone1'], 'phone2':p['phone2'], 
                           'im_handle':p['im_handle'], 'id':p['contact_id']}
      if p['site_id'] not in persondict[key]['sites']:
        persondict[key]['sites'][p['site_id']] = p['site_name']
      if p['role_id'] not in persondict[key]['roles']:
        persondict[key]['roles'][p['role_id']] = p['role_title'] 
    return persondict

  def getGroupPersonDict(self, group = None, name = None):
    data = self.getGroupPersonListObj(group, name)
    persondict = {}
    for d in data:
      
      p = data[d]
      
      key = p['surname'] + p['forename'] + p['email']
      if (key in persondict) == False:
        name = p['forename'] + " " + p['surname']
        persondict[key] = {'name':name, 'email':p['email'], 'groups':{}, 'roles':{},
                           'phone1':p['phone1'], 'phone2':p['phone2'], 
                           'im_handle':p['im_handle'], 'id':p['contact_id']}
      if p['group_id'] not in persondict[key]['groups']:
        persondict[key]['groups'][p['group_id']] = p['group_name']
      if p['role_id'] not in persondict[key]['roles']:
        persondict[key]['roles'][p['role_id']] = p['role_title'] 

    return persondict

  def getAssociatedSites(self, site = None, type = None):
    #Given a site id get its parents/children
    switchval = {'parent':'child', 'child':'parent'}
    if type == 'parent' or type == 'child':
      fields = ['id','name']
      select = """select site_association.%s_site, site.name
        from site_association, site 
        where site.id = site_association.%s_site
        and site_association.%s_site = :site""" % (type, type, switchval[type])
      binds = {'site' : site}
    else:
      # FIXME: "hell" is likely to get catched as an exception (it's a str). We should probably have a proper 
      # "UncatchableException" class.
      raise "hell"

    data = {}
    try:
      data = self.getDataObject(fields, select, binds)
    except:
      self.context.Logger().message("Could not get AssociatedSites")
      data = {}
    return data

  def getResource(self, site = None, type = None):
    if type == 'CE' or type == 'SE' or type == 'SQUID':
      fields = ['id', 'fqdn', 'is_primary']
      select ="""select id, fqdn, is_primary
        from resource_element
        where site = :site and type = :type
        order by is_primary desc"""
      binds = {'site' : site, 'type' : type}
      data = {}
      try:
        data = self.getDataObject(fields, select, binds)
      except:
        self.context.Logger().message("Could not get ResouceList")
        data = {}
      return data
    else:
      raise "hell" #TODO: UnknownResourceType Exception

  def getPhEDExNodes (self, site = None):
    fields = ['node']
    select = "select name from phedex_node where site = :site order by name"
    binds = { 'site' : site }
    data = {}
    try:
      data = self.getDataObject(fields, select, binds)
    except:
      self.context.Logger().message("Could not get PhEDExNodes")
      data = {}
    return data
  
  def getSiteInfo(self, site = None):
    #TODO: Update to use PhEDEx node table - data dictionary to contain a list of PhEDEx nodes
    fields = ['name', 'id', 'tier', 'country', 'usage', 'url', 'logo', 'gocid', 'devel', 'manual']
    select = """select site.name, site.id, tier.name, site.country, site.usage, 
     site.url, site.logourl, site.gocdbid, site.getdevlrelease, site.manualinstall
    from site join tier on tier.id = site.tier
     where site.id = :site"""
    binds = {'site' : site}
    data = {}
    try:
      data = self.getDataObject(fields, select, binds)
    except:
      
      self.context.Logger().message("Could not get SiteInfo")
      data = {}
    return data

  def getSiteList(self, naming_scheme = "name"):
    data = self.getSiteListObj(naming_scheme)
    sitelist = {}
    tier0 = []
    tier1 = []
    tier2 = []
    tier3 = []
    tier4 = []
    d=0
    while d < len(data):
      s=data[d]
      if s['tier'] == "Tier 0":
        site = {'id': s['id'], 'name': s['name']}
        tier0.append(site)
      elif s['tier'] == "Tier 1":
        site = {'id': s['id'], 'name': s['name']}
        tier1.append(site)
      elif s['tier'] == "Tier 2":
        site = {'id': s['id'], 'name': s['name']}
        tier2.append(site)
      elif s['tier'] == "Tier 3":
        site = {'id': s['id'], 'name': s['name']}
        tier3.append(site)
      else:
        site = {'id': s['id'], 'name': s['name']}
        tier4.append(site)
      d += 1
    sitelist = {'tier0': tier0, 'tier1': tier1, 'tier2': tier2, 
                'tier3': tier3, 'tier4': tier4}
    return sitelist

  def addGroup(self, group = None):
    #TODO: Update to use PhEDEx node table - data dictionary to contain a list of PhEDEx nodes
    binds = {'group' : group}
    data = {}
    try:
        if self.connectionType() ==  "sqlite":
            insert_sqlite = "insert into user_group (name) values(:group)"
            self.editDataObject(insert_sqlite, binds)
        elif self.connectionType() == "oracle":
            insert_oracle = "insert into user_group (name, id) values(:group, user_group_sq.nextval)"
            self.editDataObject(insert_oracle, binds)
        else:
            self.context.Logger().message("Unknown database type!")
    except Exception, e:
      self.context.Logger().message("Could not get SiteInfo %s" % e)
      data = {}
    return data

  def addRole(self, role = None):
    #TODO: Update to use PhEDEx node table - data dictionary to contain a list of PhEDEx nodes
    binds = {'role' : role}
    data = {}
    try:
        if self.connectionType() ==  "sqlite":
            insert_sqlite = "insert into role (title) values(:role)"
            self.editDataObject(insert_sqlite, binds)
        elif self.connectionType() == "oracle":
            insert_oracle = "insert into role (title, id) values(:role, role_sq.nextval)"
            self.editDataObject(insert_oracle, binds)
        else:
            self.context.Logger().error ("Unknown database type!")
    except Exception, e:
      self.context.Logger().message("Could not get SiteInfo: %s" % e)
      data = {}
    return data
  
class SiteDBPerson:
# Simple class to hold person information 
#TODO: Subclass to make a persistent version
  id = ''             # Number
  forename = ''       # String 
  surname = ''        # String
  email = ''          # String
  phone1 = ''         # String
  phone2 = ''         # String
  roles = {}          # dictionary of role_id(int):role_name(string)
  sites = {}          # dictionary of site_id(int):site_name(string)
  responsibilty = {}  # dictionary of site_id(int):(role_id(int)'s)
  
  def getRoles(self, site=None):
    # Get the roles associated with the person for a given site. If
    # no site is specified all roles held by the person are returned.
    assert False and "TO BE IMPLEMENTED"
    return
  
  def addRole(self, role=None, site=None):
    # Add a new role to a person, role is an int for the role id
    # Site is the id of the site the person has the role for.
    if site == None or role == None:
      raise "No site or role information given"
    else:
      rolelist = responsibilty[site].append(role)
      responsibilty = {site: rolelist}
      return
  
  def removeRole(self, role=None, site=None):
    # Add a new role to a person, role is a dictionary of role_id:role_name.
    # Site is the id of the site the person has the role for
    return
  
  def getSites(self, role=None):
    # Returns a dictionary of all sites associated with the person.
    return
  
class _ConnectionHolder:
  #Could make this smarter....
  con = ''
  database = '' 
  type = '' 
    
class SiteResources (object):
  context = None
  db = None
  id = 0  
  name = ''
  pledge = {}

  def __init__(self, context, site = 0):
    self.pledge = {'cpu - kSI2k': 0,
  'job_slots - #':0,
  'disk_store - TB': 0,  
  'tape_store - TB': 0,  
  'wan_store - TB': 0,  
  'local_store - TB': 0,  
  'national_bandwidth - Gbps': 0,  
  'opn_bandwidth - Gbps': 0 } 
    #self.pledge = {}
    self.context = context
    self.db = self.context.SiteDBApi ()
    if site:
        if int(site) > 0:
          self.context.Logger().message("site: %s" % site)
          self.id = site
          self.name = self.db.getSiteInfo(self.id)[0]['name']
          self.context.Logger().message("Site resources for %s being loaded" % (self.name))
    else:
      self.context.Logger().message("No site specified doing global pledge")
      self.id = 0 #Just in case....
      
  def publicResources(self, quarter, year):
    select = ""
    binds = {}
    fields = []
    if not year: year = date.today().year
    if not quarter: quarter = date.today().month
    #TODO: Get resource delivered, too
    pledgequarter = float(year) + (float(quarter) / 10.0)
    if self.id == 0:
      #TODO: Test this SQL with Oracle 
      select = """
  select 
    sum(cpu) keep (dense_rank last order by pledgedate asc), 
    sum(job_slots) keep (dense_rank last order by pledgedate asc),
    sum(disk_store) keep (dense_rank last order by pledgedate asc),
    sum(tape_store) keep (dense_rank last order by pledgedate asc),
    sum(wan_store) keep (dense_rank last order by pledgedate asc),
    sum(local_store) keep (dense_rank last order by pledgedate asc),
    sum(national_bandwidth) keep (dense_rank last order by pledgedate asc),
    sum(opn_bandwidth) keep (dense_rank last order by pledgedate asc)
  from resource_pledge 
  where pledgequarter = :pledgequarter
  group by site;
      """
      binds = {'pledgequarter': pledgequarter}
      fields = ['cpu', 'job_slots', 'disk_store', 'tape_store', 'wan_store', 'local_store', 'national_bandwidth', 'opn_bandwidth']
    else:
      select = """
select
    max(PLEDGEQUARTER),
    cpu, job_slots, disk_store, tape_store, wan_store, local_store, 
    national_bandwidth, opn_bandwidth
from resource_pledge
where site = :site
and pledgedate in (
    select
        max(pledgedate) from RESOURCE_PLEDGE where site = :site and pledgequarter <= :pledgequarter
    group by PLEDGEQUARTER
)
group by cpu, job_slots, disk_store, tape_store, wan_store, local_store, 
    national_bandwidth, opn_bandwidth

order by max(PLEDGEQUARTER) desc"""
      binds = {'site' : self.id, 'pledgequarter': pledgequarter}
      fields = ['PLEDGEQUARTER','cpu', 'job_slots', 'disk_store', 'tape_store', 'wan_store', 'local_store', 'national_bandwidth', 'opn_bandwidth']
    data = {}
     
    try:
      if self.id > 0:# TODO: Get clever Oracle select working and add in or self.db.connectionType() == "oracle":
        data = self.db.getDataObject(fields, select, binds)
      else:
        resource_sites = self.db.getDataObject('site', 'select distinct site from resource_pledge')
        for s in resource_sites:
          select = """
  select
    cpu, job_slots, disk_store, tape_store, wan_store, local_store, national_bandwidth, opn_bandwidth 
  from resource_pledge
  where 
    site = :site
  and pledgequarter = :pledgequarter
  order by pledgedate desc
  """
          binds = {'site' : resource_sites[s]['site'], 'pledgequarter': pledgequarter}
          sqlitedata = self.db.getDataObject(fields, select, binds)
          if len(sqlitedata) > 0:
            for k in self.pledge.keys():
              key = k.split()[0]
              if sqlitedata[0][key]:
                self.pledge[k] += sqlitedata[0][key]
    except Exception, e:
      self.context.Logger().debug(e)
      self.context.Logger().debug(fields)
      self.context.Logger().debug(select)
      self.context.Logger().debug(binds)

      self.context.Logger().message("Could not get site resource information")
    if len(data) > 0:
      for k in self.pledge.keys():
        key = k.split()[0]
        self.pledge[k] = data[0][key]

  def commit(self, binds):
    insert = ''
    binds['pledgequarter'] = binds['year'] + "." + binds['quarter']
    binds.pop('year')
    binds.pop('quarter')
    
    if self.db.connectionType() == "sqlite":
      insert = """
insert into resource_pledge
  (site, cpu, job_slots, disk_store, tape_store, wan_store, local_store, national_bandwidth, opn_bandwidth, pledgequarter) 
values
  (:siteid, :cpu, :job_slots, :disk_store, :tape_store, :wan_store, :local_store, :national_bandwidth, :opn_bandwidth, :pledgequarter)"""
    elif self.db.connectionType() == "oracle":
      insert = """
insert into resource_pledge
  (pledgeid, site, cpu, job_slots, disk_store, tape_store, wan_store, local_store, national_bandwidth, opn_bandwidth, pledgedate, pledgequarter) 
values
  (resource_pledge_sq.nextval, :siteid, :cpu, :job_slots, :disk_store, :tape_store, :wan_store, :local_store, :national_bandwidth, :opn_bandwidth, systimestamp, :pledgequarter)"""
    else:
      self.context.Logger().message("%s is of unknown database type" % self.db)
    print self.db.editDataObject(insert, binds)
    try:
      self.db.editDataObject(insert, binds)
    except:
      self.context.Logger().message("Could not update site resource information")
  
class SiteSurvey:
    def __init__(self, context):
        self.context = context
        self.db = self.context.SiteDBApi()
        
    def surveyCount(self):
        timestamp = time.mktime(datetime.now().timetuple())
        return {'total':self.db.getDataObject(['count'], "select count(name) from survey")[0]['count']
                , 'open':self.db.getDataObject(['count'], "select count(name) from survey where closed > :timestamp", {"timestamp":str(timestamp)})[0]['count']}

    def getSurveyList(self):
        select = "select name from survey"
        surveydict = self.db.getDataObject(['name'],select)
        surveylist = []
        return surveylist
            
    def newSurvey(self, duration, start, name, creator, sitewho):#, group): 
    #TODO: Extend to group surveys, too
        end = datetime.fromtimestamp(float(start)) + timedelta(weeks=float(duration))
        end = time.mktime(end.timetuple())
        insert = ""
        if self.db.connectionType() == "sqlite":
            insert = """insert into survey (name, creator, opened, closed) 
            values (:surv_name, :surv_creator, :surv_start, :surv_end)"""
        elif self.db.connectionType() == "oracle":
            insert = """insert into survey (id, name, creator, opened, closed)
            values (survey_sq.nextval, :surv_name, :surv_creator, :surv_start, :surv_end)"""
        binds = {'surv_name': name, 'surv_creator': creator, 'surv_start': str(start), 'surv_end': str(end)}
        self.db.editDataObject(insert, binds)
        fields = ['id']
        select = """select id from survey where 
        opened = :surv_start and 
        closed = :surv_end and 
        name = :surv_name and
        creator = :surv_creator"""
        id = self.db.getDataObject(fields, select, binds)[0]['id']
        
        inserttier = ''
        insertrole = ''
        if type(sitewho) == type("str"):
            insert = """insert into survey_who (survey, tier, role) 
            values (:surv_id, :surv_tier, :surv_role)"""
            binds = {'surv_id': id,"surv_tier": sitewho.split('_')[0], "surv_role": sitewho.split('_')[1]}
            self.db.editDataObject(insert, binds)
        else:    
            for w in sitewho:
                insert = "insert into survey_who (survey, tier, role) values (:surv_id, :surv_tier, :surv_role)"
                binds = {'surv_id': id,"surv_tier": w.split('_')[0],"surv_role": w.split('_')[1]}
                self.db.editDataObject(insert, binds)
        #print binds
        #print select
        #print self.db.getDataObject(fields, select, binds)
        return id

    def newQuestion(self, survey, text, answertype):
        insert = ""
        if self.db.connectionType() == "sqlite":
            insert = """insert into question (survey, question, response)
            values (:surv_id, :question, :response)"""
        elif self.db.connectionType() == "oracle":
            insert = """insert into question (id, survey, question, response)
            values (question_sq.nextval, :surv_id, :question, :response)"""
        binds = {'surv_id':survey, 'question':text, 'response':answertype}
        self.db.editDataObject(insert, binds)
        
    def getQuestionList(self, survey):
        select = "select question from question where survey = :surv_id"
        binds = {"surv_id": survey}
        questiondict = self.db.getDataObject(['question'],select,binds)
        questionlist = []
        for q in questiondict:
            questionlist.append(" ".join(questiondict[q]['question'].split()[:10]))
        return questionlist
        
    def getAllQuestions(self, survey):
        select = "select id, question, response from question where survey = :surv_id"
        binds = {"surv_id": survey}
        return self.db.getDataObject(['id', 'question', 'type'],select, binds)
    
    def getFullSurveyList(self):
        select = """select survey.id, survey.name, survey_who.role, survey_who.tier 
            from survey
            join survey_who on survey_who.survey = survey.id
            and survey.closed > :timestamp"""
        timestamp = time.mktime(datetime.now().timetuple())
        data = self.db.getDataObject(['id','name','role','tier'], select, {"timestamp":str(timestamp)})
        surveylist = {}
        roles = self.db.getDataObject(['id','title'], "select id, title from role")
        tiers = self.db.getDataObject(['id','name'], "select id, name from tier")
        roledict={}
        for r in roles:
            roledict[roles[r]['id']] = roles[r]['title']
        tierdict={100:'All Tiers'}
        for r in tiers:
            tierdict[tiers[r]['id']] = tiers[r]['name']
        for d in data:
            if not data[d]['id'] in surveylist:
                whotuple = [roledict[data[d]['role']], tierdict[data[d]['tier']]]
                surveylist[data[d]['id']] = {'name':data[d]['name'], 
                                             'wholist':[whotuple]}
            else:
                whotuple = [data[d]['role'],data[d]['tier']]
                if whotuple not in surveylist[data[d]['id']]['wholist']:
                    surveylist[data[d]['id']]['wholist'].append(whotuple)
        return surveylist
    
    def getSurvey(self, id):
        select = "select name, closed from survey where id = :surv_id"
        return self.db.getDataObject(['name','closed'], select, {"surv_id":id})
    
    def addAnswer(self, site, question, answer, user):
        insert = """insert into question_answer (id, site, question, answer, sdbuser)
        values (question_sq.nextval, :ans_site, :ans_qid, :answer, :sdbuser)"""
        binds = {'ans_site': site, 'ans_qid': question, 'answer': answer, 'sdbuser': user}
        self.db.editDataObject(insert, binds)
    
class SAM:
    def __init__(self, endpoint=None, cert=None, key=None):
        self.endpoint = endpoint 
        self.cert = cert
        self.key = key
        
    def getCMSSWInstalls(self, ce=None):
        sam = urllib.URLopener(cert_file=self.cert, key_file=self.key)
        url = "%sfunct=TestResultLatest&nodename=%s&vo=cms&testname=CE-cms-swinst" % (self.endpoint, ce)
        software = ''
        pageSoup = BeautifulSoup(sam.open(url).read())
        swlists = pageSoup.findAll('ol', { "class" : "CMSSW-list"})
        
        software = {}
        for tag in pageSoup.findAll('ol', { "class" : "CMSSW-list"}):
            children=[]
            for i in tag.contents:
                child = i.string
                if child != '\n' and child != 'error':
                    children.append(child)
                
            children.sort()
            children.reverse()
            software[tag['id']] = children
        return software
        
