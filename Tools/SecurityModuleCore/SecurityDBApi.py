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

from datetime import datetime, timedelta
from time import strptime, strftime

from os import getenv

from Crypto.Cipher import Blowfish
from base64 import b64encode, b64decode
import crypt
import re
    
class SecurityDBApi(object):
    
  def __init__(self, context):
    """The constructor of the SecurityDBApi creates a SiteDBApi, connects to the sitedb instance
        and puts it on the context so that it is available for others to use
    """
    self.api = SiteDBApi (context)
    self.api.connect ()
    context.addService (self.api)
    
  def _first(self, cur):
    row = cur.fetchone()
    if row: return row[0]
    else: return None

  def getDNFromUsername(self, username):
    fields = ("dn")    
    return self.api.getDataObject (fields, 
      '''select dn from contact where username = :username''',
      { 'username' : username })

  def getPasswordFromUsername(self, username):
    fields = ("passwd")
    return self.api.getDataObject (fields,
      '''select passwd from user_passwd where username = :username''',
      { 'username' : username })
  
  def getUsernameFromDN(self, dn):
    fields = ("username")
    return self.api.getDataObject (fields, '''select username from contact where dn = :dn''',
                            { 'dn' : dn })
  
  def getAllFromID(self, id):
    fields = ("dn", "username", "passwd")
    return self.api.getDataObject (fields, 
        '''select c.dn, c.username, p.passwd
           from contact c left join user_passwd p on p.username = c.username
           where c.id = :id''',
           { 'id' : id })

  def getUsernameFromID(self, id):
    fields = ("username")
    return self.api.getDataObject (fields, 
        '''select username from contact where id = :id''',
           { 'id' : id })[0]["username"]
    
  def getDNFromID(self, id):
    fields = ("dn")
    return self.api.getDataObject (fields, 
        '''select dn from contact where id = :id''',
           { 'id' : id })[0]["dn"]

  def getIDFromUsername(self, username):
    fields = ("id")
    return self.api.getDataObject (fields, 
        '''select id from contact where username = :username''',
           { 'username' : username })[0]["id"]
    
  def getIDFromDN(self, dn):
    fields = ("id")
    return self.api.getDataObject (fields, 
        '''select id from contact where dn = :dn''',
           { 'dn' : dn })[0]["id"]           
    
  def getCryptoKey(self, id): #id comes from cookie
      fields = ("timestamp", "key")
      keyinfo = self.api.getDataObject(fields, 
        '''select time, cryptkey
        from crypt_key
        where id = :id''', {"id": id})
      return keyinfo[0]
  
  def addCryptoKey(self, key): 
      #store key to database, return the key id:
      if self.api.connectionType() == "sqlite":
          self.api.editDataObject("""insert into crypt_key (cryptkey) values (:key)""", 
                                  {"key":key})
      elif self.api.connectionType() == "oracle" or self.api.connectionType() == "SQLAlchemy":
          self.api.editDataObject("""insert into crypt_key (cryptkey, time, id) values (:key, systimestamp, crypt_key_sq.nextval)""", 
                                  {"key":key})
      fields = ("id")
      keyinfo = self.api.getDataObject(fields, 
        '''select id from crypt_key where cryptkey = :key''', {"key": key})
      return keyinfo[0]['id']
  
  def hasGroupResponsibility (self, username, group, role):
    self.api.context.Logger().debug( "Does %s have %s for group %s" % (username, role, group) ) 
    fields = ("count")
    try:
        self.api.context.Logger().debug ( "Connection type = %s" % self.api.connectionType() )
        data = ''
        if self.api.connectionType() == "sqlite":
            self.api.context.Logger().debug( "Has group responsibility" )
            groupsplit = group.replace("|", "', '")
            self.api.context.Logger().debug( groupsplit )
            rolesplit = role.replace("|", "', '")
            self.api.context.Logger().debug( rolesplit )
            sql = """SELECT count (contact.id)
      FROM group_responsibility
      JOIN contact on contact.id = group_responsibility.contact
      JOIN role on role.id = group_responsibility.role
      JOIN user_group on user_group.id = group_responsibility.user_group
      WHERE contact.username = :sdb_username
      AND role.title in ('%s')
      AND user_group.name in ('%s')"""% (rolesplit, groupsplit)
            data = self.api.getDataObject (fields, sql, {"sdb_username": username})    
            self.api.context.Logger().debug( "count = %s" % data )   
        elif self.api.connectionType() == "oracle":
            data = self.api.getDataObject (fields,
    """SELECT count (contact.id)
      FROM group_responsibility
      JOIN contact on contact.id = group_responsibility.contact
      JOIN role on role.id = group_responsibility.role
      JOIN user_group on user_group.id = group_responsibility.user_group
      WHERE contact.username = :sdb_username
      AND REGEXP_LIKE(role.title, :sdb_role) 
      AND REGEXP_LIKE(user_group.name, :sdb_group)""", {"sdb_username": username,
                                        "sdb_group": group,
                                        "sdb_role": role})
        if data[0]["count"]:
            return True
    except:
        return False
    return False
  
  # site can be either the site name or the site id
  def hasSiteResponsibility (self, username, site, role):
    self.api.context.Logger().debug( "Does %s have %s for site %s" % (username, role, site) )
    fields = ("count")
    try:
        data = {} 
        if site:
            if not site.isdigit():       
                if self.api.connectionType() == "sqlite":
                    sitesplit = site.replace("|", "', '")
                    self.api.context.Logger().debug( sitesplit )
                    rolesplit = role.replace("|", "', '")
                    self.api.context.Logger().debug( rolesplit )
                    sql = """SELECT count (contact.id)
              FROM site_responsibility
              join contact on contact.id = site_responsibility.contact
              join role on role.id = site_responsibility.role
              join site on site.id = site_responsibility.site
              WHERE contact.username = :sdb_username
              AND role.title in ('%s')
              AND site.name in ('%s')""" % (rolesplit, sitesplit)
                  
                    data = self.api.getDataObject (fields, sql, {"sdb_username": username})            
                elif self.api.connectionType() == "oracle":
                    data = self.api.getDataObject (fields,
            """SELECT count (contact.id)
              FROM site_responsibility
              join contact on contact.id = site_responsibility.contact
              join role on role.id = site_responsibility.role
              join site on site.id = site_responsibility.site
              WHERE contact.username = :sdb_username
              AND REGEXP_LIKE(role.title, :sdb_role) 
              AND REGEXP_LIKE(site.name, :sdb_site)""", {"sdb_username": username,
                                                "sdb_site": site,
                                                "sdb_role": role})
            else:
                if self.api.connectionType() == "sqlite":
                    sitesplit = site.replace("|", "', '")
                    self.api.context.Logger().debug( sitesplit )
                    rolesplit = role.replace("|", "', '")
                    self.api.context.Logger().debug( rolesplit )
                    sql = """SELECT count (contact.id)
              FROM site_responsibility
              join contact on contact.id = site_responsibility.contact
              join role on role.id = site_responsibility.role
              join site on site.id = site_responsibility.site
              WHERE contact.username = :sdb_username
              AND role.title in ('%s')
              AND site.id in ('%s')""" % (rolesplit, sitesplit)
                    data = self.api.getDataObject (fields, sql, {"sdb_username": username})            
                elif self.api.connectionType() == "oracle":
                    data = self.api.getDataObject (fields,            
            """SELECT count (contact.id)
              FROM site_responsibility
              join contact on contact.id = site_responsibility.contact
              join role on role.id = site_responsibility.role
              join site on site.id = site_responsibility.site
              WHERE contact.username = :sdb_username
              AND REGEXP_LIKE(role.title, :sdb_role)
              AND REGEXP_LIKE(site.id, :sdb_site)""", {"sdb_username": username,
                                                "sdb_site": site,
                                                "sdb_role": role})
            if data[0]["count"]:
                self.api.context.Logger().debug( "%s has role %s for site %s" % (username, role, site) )
                return True
    except Exception, e:
      self.api.context.Logger().debug( e )
      return False
    return False

  def hasSite(self, username, site):
      fields = ("count")
      if not site.isdigit():
          data = self.api.getDataObject (fields,
    """SELECT count (contact.id)
      FROM site_responsibility
      join contact on contact.id = site_responsibility.contact
      join site on site.id = site_responsibility.site
      WHERE contact.username = :sdb_username
      AND site.name = :sdb_site""", {"sdb_username": username,
                                        "sdb_site": site})
      else:
          data = self.api.getDataObject (fields,
    """SELECT count (contact.id)
      FROM site_responsibility
      join contact on contact.id = site_responsibility.contact
      join site on site.id = site_responsibility.site
      WHERE contact.username = :sdb_username
      AND site.id = :sdb_site""", {"sdb_username": username,
                                        "sdb_site": site})
      if data[0]["count"]:
          return True
      return False
  
  def hasGroup (self, username, group):
    fields = ("count")
    data = self.api.getDataObject (fields,
    """SELECT count (contact.id)
      FROM group_responsibility
      JOIN contact on contact.id = group_responsibility.contact
      JOIN user_group on user_group.id = group_responsibility.user_group
      WHERE contact.username = :username
      AND user_group.name = :group""", {"username": username,
                                        "group": group})
    if data[0]["count"]:
      return True
    return False
  
  def hasRole (self, username, role):
    fields = ("count")
    data = self.api.getDataObject (fields,
    """SELECT count (contact.id)
      FROM group_responsibility
      JOIN contact on contact.id = group_responsibility.contact
      JOIN role on role.id = group_responsibility.role
      WHERE contact.username = :username
      AND role.title = :role""", {"username": username,
                                        "role": role})
    if data[0]["count"]:
      return True
    data = self.api.getDataObject (fields,
    """SELECT count (contact.id)
      FROM site_responsibility
      join contact on contact.id = site_responsibility.contact
      join role on role.id = site_responsibility.role
      WHERE contact.username = :username
      AND role.title = :role""", {"username": username,
                                        "role": role})
    if data[0]["count"]:
      return True  
    return False

  def groupsForRole (self, username, role):
    fields = ("id", "group")
    data = self.api.getDataObject (fields,
    """SELECT user_group.id, user_group.name 
       FROM user_group
       JOIN group_responsibility on group_responsibility.user_group = user_group.id
       JOIN contact on contact.id = group_responsibility.contact
       JOIN role on role.id = group_responsibility.role
       WHERE contact.username = :username
       AND role.title = :role""",{"username": username,
       "role": role})
    return data

  def rolesForGroup (self, username, group):
    fields = ("id", "roles")
    data = self.api.getDataObject (fields,
    """SELECT role.id, role.title
       FROM role
       join contact on contact.id = group_responsibility.contact
       join group_responsibility on group_responsibility.role = role.id
       JOIN user_group on user_group.id = group_responsibility.user_group
       WHERE contact.username = :username
       AND user_group.name = :group""",{"username": username,
       "group": group})
    return data

  def sitesForRole(self, username, role):
    fields = ("id", "sites")
    data = self.api.getDataObject (fields,
    """SELECT site.id, site.name
       FROM site
       join site_responsibility on site_responsibility.site = site.id
       join contact on contact.id = site_responsibility.contact
       join role on role.id = site_responsibility.role
       WHERE contact.username = :username
       AND role.title = :role""",{"username": username,
       "role": role})
    return data  

  def rolesForSite(self, username, site):
    fields = ("id", "roles")
    if not site.isdigit():
        data = self.api.getDataObject (fields,
    """SELECT role.id, role.title
       FROM role
       join contact on contact.id = site_responsibility.contact
       join site_responsibility on site_responsibility.role = role.id 
       join site on site.id = site_responsibility.site
       WHERE contact.username = :username
       AND site.name = :site""",{"username": username,
       "site": site})
    else:
        data = self.api.getDataObject (fields,
    """SELECT role.id, role.title
       FROM role
       join contact on contact.id = site_responsibility.contact
       join site_responsibility on site_responsibility.role = role.id 
       join site on site.id = site_responsibility.site
       WHERE contact.username = :username
       AND site.id = :site""",{"username": username,
       "site": site})        
    return data

  def importHNAccount (self, surname, forename, username, passwd, email):
    # First we try to insert a new user. If that fails, we only try to update the
    # password.
    try:
      #See if a person already exists and check the username  
      result = self.api.getDataObject(("id", "username", "forename", "surname"),
                                      """select id, username, forename, surname 
                                      FROM contact 
                                      WHERE surname=:s and forename=:f""",
                                      {"s":surname, "f":forename})
      if len(result) == 0:
          #Person doesn't exist yet so add them in
          if email == None:
          # Schema requires an email address so take a guess (if we can't get it from HN)
              email=surname + "@mail.cern.ch"
          self.api.context.Logger().message ("Adding user %s (%s %s - %s)" % (username, forename, surname, email))
          try: 
              result = self.api.editDataObject ("""
              INSERT into contact (surname, forename, email, username, id)
              VALUES (:surname, :forename, :email, :username, contact_sq.nextval)""", 
              {"surname": surname,
               "forename": forename,
               "email": email,
               "username": username})
          except Exception,e:
              self.api.context.Logger().message ("Can't insert to contact for %s" % username)
          try: 
              result = self.api.editDataObject ("""
              INSERT into user_passwd (username, passwd)
              VALUES (:username, :passwd)""", 
              {"username": username,
               "passwd": passwd})
          except Exception, e:  
              self.api.context.Logger().message ("Can't insert to user_password for %s" % username)
      else:
          #Person exists, so update their username and password
          self.api.context.Logger().message ("User %s is already in DB. Updating password." % username)          
          try:     
              self.api.editDataObject ("""
              INSERT into user_passwd (username, passwd)
              VALUES (:username, :passwd)""", 
              {"username": username,
               "passwd": passwd})      
          except Exception, e:  
              self.api.context.Logger().message ("Can't insert %s into user_password " % username)
              self.api.context.Logger().debug ( e )    
              self.api.context.Logger().message ("Attempting to update username and password for %s %s" % (forename, surname))
              try:
                  self.api.editDataObject ("""
                                                  UPDATE user_passwd 
                                                  SET passwd=:passwd
                                                  WHERE username=:username""", 
                                                  {"username": username,
                                                   "passwd": passwd})
              except Exception, e:
                  self.api.context.Logger().message ("Can't update user_password for %s" % username)
          self.api.context.Logger().message ("Updating contact table")
          try:
              self.api.context.Logger().debug (result[0]['id'])
              binds = {"id": result[0]['id'], "username": username}
              self.api.editDataObject ("""
              UPDATE contact set username=:username 
              WHERE id = :id""", 
              binds)
          except Exception,e:
              self.api.context.Logger().message ( "Ooops, problem updating username to %s for %s %s" % (username, forename, surname) )  
              self.api.context.Logger().debug ( e )            
          
      self.api.context.Logger().message ("User %s added to db." % username)
    except Exception, e:
      # If an exception is raised we only update the passwd.
      # DN and username are unique, but can be Null. If a 
      # DN/username exists the contact will have an email, 
      # surname and forename (all not null, but not necessarily unique).
      self.api.context.Logger().message ( "Ooops, problem with user %s (%s %s)" % (username, forename, surname) )
      self.api.context.Logger().debug ( e )
      
  def getAllUserIds(self):
      #Return all user ID's of existing users
      fields = ("id")
      data = self.api.getDataObject (fields, 
        '''select id from contact''',
           {})
      allUsers = []
      for d in data:
          allUsers.append(data[d]["id"])
      return allUsers
  
  def getAllUsernames(self):
      #Return all user ID's of existing users
      fields = ("username")
      data = self.api.getDataObject (fields, 
        '''select username from contact''',
           {})
      allUsers = []
      for d in data:
          allUsers.append(data[d]["username"])
      return allUsers
  
  def getAllRoles(self, user):
      pass
  
  def grantUserSiteRole(self, user, site, role):
      "user is the user id, site is site id, role is role id"
      sql = "insert into SITE_RESPONSIBILITY ( CONTACT, ROLE, SITE ) VALUES (:sdb_user, :sdb_role, :sdb_site)"
      binds ={'sdb_user': user, 'sdb_site': site, 'sdb_role': role}
      self.api.editDataObject(sql, binds)
      
  def rescindUserSiteRole(self, user, site, role):
      "user is the user name, site is site name, role is role name"
      sql = "delete from SITE_RESPONSIBILITY where CONTACT=:sdb_user AND SITE=:sdb_site AND ROLE=:sdb_role"
      binds ={'sdb_user': user, 'sdb_site': site, 'sdb_role': role}
      self.api.editDataObject(sql, binds)
  
  def grantUserGroupRole(self, user, group, role):      
      "user is the user name, group is group name, role is role name"
      sql = "insert into GROUP_RESPONSIBILITY( CONTACT, ROLE, USER_GROUP ) VALUES (:sdb_user, :sdb_role, :sdb_group)"
      binds ={'sdb_user': user, 'sdb_group': group, 'sdb_role': role}
      self.api.editDataObject(sql, binds)
      
  def rescindUserGroupRole(self, user, group, role):
      "user is the user name, site is site name, role is role name"
      sql = "delete from GROUP_RESPONSIBILITY where CONTACT=:sdb_user AND USER_GROUP=:sdb_group AND ROLE=:sdb_role"
      binds ={'sdb_user': user, 'sdb_group': group, 'sdb_role': role}  
      self.api.editDataObject(sql, binds)