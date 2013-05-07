#!/usr/bin/env python
import sys
import os
import ConfigParser
from optparse import OptionParser
import crypt

class CreateSiteDBHelper:
  def getPath(self):
    path = __file__.replace(__file__.split('/')[-1], '')
    splitter = -1 * path.count("../")
    path = path.replace("../", '')
    newpath = "/"
    newpath = newpath.join(os.getcwd().split('/')[0:splitter]) + "/" + path
    return newpath.replace("/Utilities", "")
  
class CreateSQLiteDB(CreateSiteDBHelper):
  def __init__(self, schema=None, path=None, dbname=None, verbose=None, test=None):
    from pysqlite2 import dbapi2 as sqlite 
    if verbose:
      print "Creating database in path = " + path + dbname
      
    con = sqlite.connect(path+dbname)
    self.initSchema(con, path, dbname, verbose, test)
    self.initTables(con, path, dbname, verbose, test)
    if verbose:
      print "SQLite database exists: %s - database creation completed" % os.path.exists(path+dbname)
      
  def initSchema(self, con=None, path=None, dbname=None, verbose=None, test=None):
    if con != None:
      cur = con.cursor()
      #this next bit is fugly
      sitesql='''/**
   *  "Site" definition tables
   **/
  
  /* Site Tier as in T1, T2, T3 */
  create table tier (
    id      INTEGER not null PRIMARY KEY AUTOINCREMENT,
    pos      number(10) not null,
    name      varchar(100) not null,
    --
    constraint uk_tier_pos unique (pos),
    constraint uk_tier_name unique (name)
  );
  
  
  
  /* Site definition and associated data */
  create table site (
    id      INTEGER not null PRIMARY KEY AUTOINCREMENT,
    name      varchar(100) not null,
    tier      number(10) not null,
    country    varchar(100) not null,
    gocdbid    number(10),
    usage      varchar(100),
    url      varchar(1000),
    logourl    varchar(1000),
    getdevlrelease  char(1),
    manualinstall    char(1),
    -- Probably going to need lots of othr ID's (SAM, Dashboard etc) so 
    -- maybe need a table for that, instead of making this one huge!
    --
    constraint uk_site unique (name),
    constraint fk_site_tier
      foreign key (tier) references tier (id)
      -- we don't delete tiers...
  );
  create index ix_site_tier on site (tier);
  
  
  
  /* How sites are related to one another e.g. FNAL is a parent site to Nebraska */
  create table site_association (
    parent_site    number(10) not null,
    child_site    number(10) not null,
    --
    constraint pk_site_association primary key (parent_site, child_site),
    constraint fk_site_association_parent
      foreign key (parent_site) references site (id)
      on delete cascade,
    constraint fk_site_association_child
      foreign key (child_site) references site (id)
      on delete cascade
  );
  create index ix_site_association_child on site_association (child_site);
  '''
  
      sitesql = sitesql.lower()
      sitesql = sitesql.replace('create','\n\ncreate')
      if verbose:
        print "Creating Site tables"
      for s in sitesql.split('\n\n'):
        cur.execute(s)
  
      res_and_monsql='''
/* Site's official resource pledge */
create table resource_pledge (
  pledgeid            INTEGER not null PRIMARY KEY AUTOINCREMENT,
  pledgedate          timestamp,
  pledgequarter       float,
  site                number(10) not null,
  cpu                 float,
  job_slots           float,  
  disk_store          float,
  tape_store          float,
  wan_store           float,
  local_store         float,
  national_bandwidth  float,
  opn_bandwidth       float,
  status              char(1),
  --
  constraint fk_resource_pledge_site
    foreign key (site) references site (id)
    on delete cascade
);
CREATE TRIGGER insert_resource_pledge_pledgedate AFTER INSERT ON resource_pledge
BEGIN
  UPDATE resource_pledge SET pledgedate = DATETIME('NOW')
  WHERE rowid = new.rowid;
END;
  
  
  /* Site's resource element (disks, storage)*/
  create table resource_element (
    id      INTEGER not null PRIMARY KEY AUTOINCREMENT,
    site      number(10) not null,
    fqdn      varchar(200),
    type      varchar(100),
    is_primary    char(1),
    --
    constraint fk_resource_element_site
      foreign key (site) references site (id)
      on delete cascade
  );
  create index ix_resource_element_site on resource_element (site);
  
  
  
  /* Site's phedex nodes */
  create table phedex_node (
    id      INTEGER not null PRIMARY KEY AUTOINCREMENT,
    site      number(10) not null,
    name      varchar(100) not null,
    --
    constraint uk_phedex_node_name unique ( name),
    constraint fk_phedex_node_site
      foreign key (site) references site (id)
      -- cascade?  depends on how dependant phedex becomes on this...
  );
  create index ix_phedex_node_site on phedex_node (site);
  create index ix_phedex_node_name on phedex_node (name);
  
  
  
  /**
   *   Site performance tables
   **/
  
  /* High-level statistics about a site's performance */
  create table performance (
    site      number(10) not null,
    time      timestamp not null,
    job_quality    float,
    transfer_quality  float,
    jobrobot_quality  float,
    job_io    float,
    wan_io    float,
    phedex_io    float,
    phedex_sum_tx_in  float,
    phedex_sum_tx_out  float,
    --
    constraint pk_performance primary key (site, time),
    constraint fk_performance_site
      foreign key (site) references site (id)
      on delete cascade
  );
  
  
  
  /* High-level statistics about a sites job activity */
  create table job_activity (
    site      number(10) not null,
    time      timestamp not null,
    activity    varchar(100),
    num_jobs    number(10),
    --
    constraint pk_job_activity primary key (site, time),
    constraint fk_job_activity_site
      foreign key (site) references site (id)
      on delete cascade
  );
  '''
      
      res_and_monsql = res_and_monsql.lower()
      res_and_monsql = res_and_monsql.replace('create','\n\ncreate')
      if verbose:
        print "Creating Resource and Monitoring tables"
      for s in res_and_monsql.split('\n\n'):
        cur.execute(s)
      
      
      secmod_sql = '''
  /* List of cryptographic keys for the security module */
  create table crypt_key (
    id      INTEGER not null PRIMARY KEY AUTOINCREMENT,
    cryptkey    varchar(80) not null,
    time      timestamp
  );
  create index ix_crypt_key_cryptkey on crypt_key (cryptkey);
  create index ix_crypt_key_time on crypt_key (time);
  
  /* List of usernames and passwords for the secuirty module */
  CREATE TABLE user_passwd (
    username    varchar(60) not null,
    passwd    varchar(30) not null,
    --
    constraint pk_user_passwd primary key (username)
  );
  create index ix_user_passwd_passwd on user_passwd (passwd);
  
  /**
   *  "Person" definition tables
   **/
  
  /* A human being */
  create table contact (
    id      INTEGER not null PRIMARY KEY AUTOINCREMENT,
    surname    varchar(1000) not null,
    forename    varchar(1000) not null,
    email      varchar(1000) not null,
    username    varchar(60),
    dn      varchar(1000),
    phone1    varchar(100),
    phone2    varchar(100),
    --
    constraint uk_contact_dn unique (dn),
    constraint uk_contact_username unique (username),
    constraint fk_contact_username
      foreign key (username) references user_passwd (username)
      on delete set null
  );
  create index ix_contact_surname on contact (surname);
  create index ix_contact_forename on contact (forename);
  
  /**
  * Management roles e.g. 'PhedexSiteAdmin', 'PhedexDataManager' 
  **/
  create table role (
    id      INTEGER not null PRIMARY KEY AUTOINCREMENT,
    title      varchar(100) not null,
    --
    constraint uk_role_title unique (title)
  );
  
  /** 
   * An abstract group humans can belong to 
   * e.g. 'higgs','top','BSM','global' etc. 
   **/
  create table user_group (
    id      INTEGER not null PRIMARY KEY AUTOINCREMENT,
    name      varchar(100) not null,
    -- 
    constraint uk_user_group_name unique (name)
  );
  
  /* A mapping of humans to responsibilites associated with a site e.g. "Bob is the PhedexSiteAdmin of T4_Antartica" */
  create table site_responsibility (
    contact    number(10) not null,
    role      number(10) not null,
    site      number(10) not null,
    --
    constraint pk_site_resp primary key (contact, role, site),
    constraint fk_site_resp_contact
      foreign key (contact) references contact (id)
      on delete cascade,
    constraint fk_site_resp_role
      foreign key (role) references role (id)
      on delete cascade,
    constraint fk_site_resp_site
      foreign key (site) references site (id)
      on delete cascade
  );
  create index ix_site_resp_role on site_responsibility (role);
  create index ix_site_resp_site on site_responsibility (site);
  
  /* A mapping of humans to responsibilities associated with a group e.g. "Joe is the ProdRequestManager of the Gravitino group */
  create table group_responsibility (
    contact    number(10) not null,
    role      number(10) not null,
    user_group    number(10) not null,
    --
    constraint pk_group_resp_contact primary key (contact, role, user_group),
    constraint fk_group_resp_contact
      foreign key (contact) references contact (id)
      on delete cascade,
    constraint fk_group_resp_role
      foreign key (role) references role (id)
      on delete cascade,
    constraint fk_group_resp_user_group
      foreign key (user_group) references user_group (id)
      on delete cascade
  );
  create index ix_group_resp_role on group_responsibility (role);
  create index ix_group_resp_user_group on group_responsibility (user_group);
  '''
      
      secmod_sql = secmod_sql.lower()
      secmod_sql = secmod_sql.replace('create','\n\ncreate')
      if verbose:
        print "Creating Security tables"
      for s in secmod_sql.split('\n\n'):
        cur.execute(s)
      
      surveysql='''
  /**
   *  Generic survey tables
   **/
  
  /* Defines a survey and associates it with its creator */
  create table survey (
    id      INTEGER not null PRIMARY KEY AUTOINCREMENT,
    name      varchar(100) not null,
    creator    number(10),
    opened    timestamp,
    closed    timestamp,
    --
    constraint fk_survey_creator
      foreign key (creator) references contact (id)
      on delete set null
  );
  create index ix_survery_creator on survey (creator);
  
  
  
  /* For sending out surveys by tier */
  create table survey_tiers (
    survey    number(10) not null,
    tier      number(10) not null,
    --
    constraint fk_survey_tiers_survey
      foreign key (survey) references survey (id)
      on delete cascade,
    constraint fk_survey_tiers_tier
      foreign key (tier) references tier (id)
      -- we don't delete tiers
  );
  create index ix_survey_tiers_survey on survey_tiers (survey);
  create index ix_survey_tiers_tier on survey_tiers (tier);
  
  
  
  /* For sending out surveys by role */
  create table survey_roles (
    survey    number(10) not null,
    role      number(10) not null,
    --
    constraint fk_survey_roles_survey
      foreign key (survey) references survey (id)
      on delete cascade,
    constraint fk_survey_roles_role
      foreign key (role) references role (id)
      on delete cascade
  );
  create index ix_survey_roles_survey on survey_roles (survey);
  create index ix_survey_roles_role on survey_roles (role);
  
  
  
  /* A question on a survey */
  create table question (
    id      INTEGER not null PRIMARY KEY AUTOINCREMENT,
    survey    number(10) not null,
    question    varchar(4000) not null,
    form_type    varchar(100) not null,
    --
    constraint fk_question_survey
      foreign key (survey) references survey (id)
      on delete cascade
  );
  create index ix_question_survey on question (survey);
  
  
  
  /* A default answer on a survey (for checkbox or drop-down menu style questions) */
  create table question_default (
    question    number(10) not null,
    pos      number(10) not null,
    value      varchar(4000) not null,
    --
    constraint pk_question_default primary key (question, pos),
    constraint fk_question_default_question
      foreign key (question) references question (id)
      on delete cascade
  );
  
  
  
  /* A site's answer to the survey question */
  create table question_answer (
    site      number(10) not null,
    question    number(10) not null,
    answer    varchar(4000) not null,
    --
    constraint pk_question_answer primary key (site, question),
    constraint fk_question_answer_site
      foreign key (site) references site (id)
      on delete cascade,
    constraint fk_question_answer_question
      foreign key (question) references question (id)
      on delete cascade
  );
  create index ix_question_answer_question on question_answer (question);'''
  
      surveysql = surveysql.lower()
      surveysql = surveysql.replace('create','\n\ncreate')
      if verbose:
        print "Creating Survey tables"
      for s in surveysql.split('\n\n'):
        cur.execute(s)
      if test == None:
        con.commit()

  def initTables(self, con=None, path=None, dbname=None, verbose=None, test=None):
    if con != None:
      cur = con.cursor()
      INSERT_TIER0 = '''insert into tier ( pos, name) values (0, 'Tier 0')'''
      INSERT_TIER1 = '''insert into tier ( pos, name) values (1, 'Tier 1')'''
      INSERT_TIER2 = '''insert into tier ( pos, name) values (2, 'Tier 2')'''
      INSERT_TIER3 = '''insert into tier ( pos, name) values (3, 'Tier 3')'''
      INSERT_TIER4 = '''insert into tier ( pos, name) values (4, 'Opportunistic/Other')'''
       
      cur.execute(INSERT_TIER0)
      cur.execute(INSERT_TIER1)
      cur.execute(INSERT_TIER2)
      cur.execute(INSERT_TIER3)
      cur.execute(INSERT_TIER4)
      
      if verbose:
        cur.execute('select * from tier')
        print cur.fetchall()
      
      INSERT_SITE1 = '''insert into site ( gocdbid, name, tier, country, usage, url, logourl) 
          values (1, 'RAL', 2, 'the UK', 'LCG', 'https://twiki.cern.ch/twiki/bin/view/CMS/RutherfordLabs', 'http://www.cclrc.ac.uk/img/CCLRC300.jpg')'''
      INSERT_SITE2 = '''insert into site ( gocdbid, name, tier, country, usage, url) 
          values (51, 'RAL PPD', 3, 'the UK', 'LCG', 'https://twiki.cern.ch/twiki/bin/view/CMS/RutherfordLabs')'''
      INSERT_SITE3 = '''insert into site ( gocdbid, name, tier, country, usage, url) 
          values (27, 'Brightlingsea', 4, 'the UK', 'LCG', 'https://twiki.cern.ch/twiki/bin/view/CMS/RutherfordLabs')'''
      INSERT_SITE4 = '''insert into site ( gocdbid, name, tier, country, usage, url, logourl) 
          values (16, 'FNAL', 2, 'the USA', 'OSG', 'http://www.fnal.gov', 'http://lss.fnal.gov/orientation/pictures/orangelogo.gif')'''
      
      cur.execute(INSERT_SITE1)
      cur.execute(INSERT_SITE2)
      cur.execute(INSERT_SITE3)
      cur.execute(INSERT_SITE4)
  
      if verbose:
        cur.execute('select * from site order by tier')
        print cur.fetchall()
        
      INSERT_ASSOCIATION = ''' insert into site_association (parent_site, child_site) values (1, 2)'''
      cur.execute(INSERT_ASSOCIATION)
      
      if verbose:
        cur.execute('select * from site_association order by parent_site')
        print cur.fetchall() 
      
      INSERT_PHEDEX_NODES = '''insert into phedex_node ( site, name) values (1, 'T1_RAL_Buffer')'''
      cur.execute(INSERT_PHEDEX_NODES)
  
      if verbose:
        cur.execute('select * from phedex_node')
        print cur.fetchall() 
        
      scope=['global','production','higgs','top','BSM']
      for s in scope:
        INSERT_GROUPS = '''insert into user_group ( name)
      values('%s')''' % (s)
        cur.execute(INSERT_GROUPS)
      
      if verbose:
        cur.execute('select * from user_group')
        print cur.fetchall()
        
      INSERT_CONTACT1 = '''insert into contact ( surname, forename, email, dn, phone1)
          values('ST','Claire', 'clairest@cern.ch', 'n=claireST', '0123456789')'''
      
      INSERT_CONTACT2 = '''insert into contact ( surname, forename, email, dn, phone1, username)
          values('Metson', 'Simon', 'simon.metson@cern.ch', 'n=simonmetson', '0123456789', 'metson')'''
      
      INSERT_CONTACT3 = '''insert into contact ( surname, forename, email, dn, phone1)
          values('Newbold', 'Dave', 'd.newbold@cern.ch', 'n=davenewbold', '0123456789')'''
      
      INSERT_CONTACT4 = '''insert into contact ( surname, forename, email, dn, phone1)
          values('Eulisse', 'Giulio', 'giulio.eulisse@cern.ch', 'n=giulio', '0123456789')'''
          
      INSERT_CONTACT5 = '''insert into contact ( surname, forename, email, dn, phone1, username)
          values('Kreuzer', 'Peter', 'p.kreuzer@cern.ch', 'n=p.kreuzer', '0123456789', 'nuts')'''
          
      INSERT_CONTACT6 = '''insert into contact ( surname, forename, email, dn, phone1, username)
          values('Wakefield', 'Stuart', 's.wakefield@cern.ch', 'n=s.wakefield', '0123456789', 'swakef')'''
          
      cur.execute(INSERT_CONTACT1)
      cur.execute(INSERT_CONTACT2)
      cur.execute(INSERT_CONTACT3)
      cur.execute(INSERT_CONTACT4)
      cur.execute(INSERT_CONTACT5)
      cur.execute(INSERT_CONTACT6)
      
      if verbose:
        cur.execute('select * from contact')
        print cur.fetchall()
        
      INSERT_CRYPT_KEY = '''INSERT INTO crypt_key ( cryptkey) VALUES ('T05FIGVmZ2hpamtsbW5vcHFyc3R1dnd4eXphYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5emFiZGU=')'''
      cur.execute(INSERT_CRYPT_KEY)
      INSERT_PASSWORD1 = ''' insert into user_passwd (username, passwd)
        values('metson', \'''' + crypt.crypt ("admin", "fo") + '''\')'''
      INSERT_PASSWORD2 = ''' insert into user_passwd (username, passwd)
        values('swakef', \'''' + crypt.crypt ("admin", "fo") + '''\')'''  
      INSERT_PASSWORD3 = ''' insert into user_passwd (username, passwd)
        values('nuts', \'''' + crypt.crypt ("admin", "fo") + '''\')'''  
      cur.execute(INSERT_PASSWORD1)
      cur.execute(INSERT_PASSWORD2)
      cur.execute(INSERT_PASSWORD3)
      cur.execute("select * from user_passwd")
      print cur.fetchall()
      
      role=['Global Admin','Site Admin','Site Executive','PhEDEx Contact','Data Manager','Production Manager','Production Operator']
      for r in role:
        INSERT_ROLE1 = '''insert into role ( title)
          values('%s')''' % (r)
        cur.execute(INSERT_ROLE1)
      
      if verbose:
        cur.execute('select * from role')
        print cur.fetchall()
        
      INSERT_RESPONSIBILITY1 = '''insert into site_responsibility(contact, site, role) values(1, 2, 1)'''
      INSERT_RESPONSIBILITY2 = '''insert into site_responsibility(contact, site, role) values(1, 2, 3)'''
      INSERT_RESPONSIBILITY3 = '''insert into site_responsibility(contact, site, role) values(2, 2, 2)'''
      INSERT_RESPONSIBILITY4 = '''insert into site_responsibility(contact, site, role) values(2, 1, 5)'''
      INSERT_RESPONSIBILITY5 = '''insert into site_responsibility(contact, site, role) values(2, 1, 1)'''
      INSERT_RESPONSIBILITY6 = '''insert into site_responsibility(contact, site, role) values(3, 1, 3)'''
      INSERT_RESPONSIBILITY7 = '''insert into site_responsibility(contact, site, role) values(4, 1, 2)'''
      INSERT_RESPONSIBILITY8 = '''insert into group_responsibility(contact, user_group, role) values(5, 2, 6)'''
      INSERT_RESPONSIBILITY9 = '''insert into group_responsibility(contact, user_group, role) values(6, 2, 7)'''
      INSERT_RESPONSIBILITY10 = '''insert into group_responsibility(contact, user_group, role) values(2, 1, 1)'''
      INSERT_RESPONSIBILITY11 = '''insert into group_responsibility(contact, user_group, role) values(4, 1, 1)'''
                
      cur.execute(INSERT_RESPONSIBILITY1)
      cur.execute(INSERT_RESPONSIBILITY2)
      cur.execute(INSERT_RESPONSIBILITY3)
      cur.execute(INSERT_RESPONSIBILITY4)
      cur.execute(INSERT_RESPONSIBILITY5)
      cur.execute(INSERT_RESPONSIBILITY6)
      cur.execute(INSERT_RESPONSIBILITY7)
      cur.execute(INSERT_RESPONSIBILITY8)
      cur.execute(INSERT_RESPONSIBILITY9)
      cur.execute(INSERT_RESPONSIBILITY10)
      cur.execute(INSERT_RESPONSIBILITY11)
      
      if verbose:
        print "Site resps"
        cur.execute('select * from  site_responsibility')
        print cur.fetchall()
        print "Group resps"
        cur.execute('select * from  group_responsibility')
        print cur.fetchall()
        
      INSERT_RESOURCE_ELEMENT1 = '''insert into resource_element ( site, fqdn, type, is_primary)
          values(1, 'lcgce01.gridpp.rl.ac.uk', 'CE', 'y')'''
      
      INSERT_RESOURCE_ELEMENT2 = '''insert into resource_element ( site, fqdn, type, is_primary)
          values(1, 'ralsrma.rl.ac.uk', 'SE', 'y')'''
      
      INSERT_RESOURCE_ELEMENT3 = '''insert into resource_element ( site, fqdn, type, is_primary)
          values(1, 'dcache.gridpp.rl.ac.uk', 'SE', 'n')'''
      
      INSERT_RESOURCE_ELEMENT4 = '''insert into resource_element ( site, fqdn, type, is_primary)
          values(2, 'heplnx206.pp.rl.ac.uk', 'CE', 'n')'''
      
      INSERT_RESOURCE_ELEMENT5 = '''insert into resource_element ( site, fqdn, type, is_primary)
          values(2, 'heplnx201.pp.rl.ac.uk', 'CE', 'y')'''
      
      INSERT_RESOURCE_ELEMENT6 = '''insert into resource_element ( site, fqdn, type, is_primary)
          values(2, 'heplnx204.pp.rl.ac.uk', 'SE', 'y')'''
      
      cur.execute(INSERT_RESOURCE_ELEMENT1)
      cur.execute(INSERT_RESOURCE_ELEMENT2)
      cur.execute(INSERT_RESOURCE_ELEMENT3)
      cur.execute(INSERT_RESOURCE_ELEMENT4)
      cur.execute(INSERT_RESOURCE_ELEMENT5)
      cur.execute(INSERT_RESOURCE_ELEMENT6)
      
      if verbose:
        cur.execute('select * from resource_element')
        print cur.fetchall()
        
      if test == None:
        con.commit()  

  def getSQLiteSchema(self, file=None):
    """Opens the schema file (Oracle) and then creates something that SQLite will read"""
    if file == None:
      raise "hell"
    else:
      return

class CreateConfigFile(CreateSiteDBHelper):
  def __init__(self, location=None, path=None, dbname=None, verbose=None, test=None):    
    config = ConfigParser.ConfigParser()
    if verbose:
      print "Creating ini in path = " + path
      print "Using database = " + dbname
    # set a number of parameters
    config.add_section('configuration')
    if location == "CERN":
      config.set('configuration', 'abspath', '/data/SiteDB')
      config.set('configuration', 'toolspath', '/data/SiteDB/WEBTOOLS')
      config.set('configuration', 'baseurl', 'http://cmsdoc.cern.ch/cms/test/aprom/DBS/siteDB/')
      config.set('configuration', 'envir', 'production')
    else:
      config.set('configuration', 'abspath', path)
      config.set('configuration', 'toolspath', path.rstrip("/SiteDB"))
      config.set('configuration', 'baseurl', 'http://localhost:8030')
      config.set('configuration', 'envir', 'development')
    
    config.add_section('endpoint')
    config.set('endpoint', 'phedex', 'https://cmsdoc.cern.ch:8443/cms/test/aprom/phedex/tbedi/Request::Create?dest=')
    config.set('endpoint', 'dbs', 'http://cmsdbs.cern.ch/discovery/getBlocksFromSiteHelper?dbsInst=MCGlobal/Writer&site=')
    config.set('endpoint', 'goc', 'https://goc.grid-support.ac.uk/gridsite/gocdb2/index.php?siteSelect=')
    config.set('endpoint', 'cmsmon', 'http://www-ekp.physik.uni-karlsruhe.de/~rabbertz/cmsmon/web/cmsmon_site.php?')
    
    config.add_section('database')
    config.set('database', 'dbname', path + dbname)
    config.set('database', 'dbtype', 'sqlite')

    if verbose:
      config.write(sys.stdout)
    
    if test == None:
      FILE = open(path + 'sitedb.ini','w')
      config.write(FILE)
      FILE.close()    

class CreateSiteDB:
  def __init__(self):
    parser = OptionParser()
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-s", "--schema_file", dest="filename",
                  help="Schema read from SCHEMAFILE to create an SQLite database", metavar="SCHEMAFILE")
    parser.add_option("-i", "--no_ini_file", dest="inifile",
                  help="Don't create the ini file for SiteDB, as on already exists", action="store_true")
    parser.add_option("-p", "--path", dest="path", default = os.getcwd() + "/",
                  help="path to where you want the SiteDB database and/or ini file to be created. Worked out from the script location if not given.")
    parser.add_option("-d", "--dbname", dest="dbname", metavar="DATABASEFILE", default = "SiteDB",
                  help="Name of the SQLite database file. Set to SiteDB if not given")
    parser.add_option("-n", "--no_database", dest="nodb", 
                      help="Don't create an SQLite database, because one already exists", action="store_true")
    parser.add_option("-l", "--location", dest="location",
                  help="Location where you want SiteDB is running. Either set LOCATION to CERN (e.g. Production use) or your own loaction. This will determine the location of the database and ini file from where this script is run.", metavar="LOCATION")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")
    parser.add_option("-t", "--test",
                      action="store_true", dest="test")

    (options, args) = parser.parse_args()
    if not options.inifile:
      ini = CreateConfigFile(options.location, options.path, options.dbname, options.verbose, options.test)
    else:
      print "You specified the -i/--no_ini_file option, skipping creating SiteDB ini file"
    if not options.nodb:
      db = CreateSQLiteDB(options.filename, options.path, options.dbname, options.verbose, options.test)
    else:
      print "You specified the -n/--no_database option, skipping creating SiteDB database"
    
if __name__ == '__main__':
  sdb = CreateSiteDB()
    