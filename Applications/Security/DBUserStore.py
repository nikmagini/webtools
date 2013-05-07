#!/usr/bin/env python
"""
Assumes you have a database with a schema like:

CREATE TABLE user_passwd (
  username        varchar(60) not null,
  passwd        varchar(30) not null,
}

to hold the username and passwords
"""
from WMCore.Database.DBFactory import DBFactory
from UserStore import UserStore
from crypt import crypt
import logging, cherrypy

class DBUserStore(UserStore):
    def __init__(self, config):
        UserStore.__init__(self, config)
        logging.basicConfig(level = logging.DEBUG,
                format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt = '%m-%d %H:%M')
        self.logger = logging.getLogger('OIDDBUserStore')
        self.conn = DBFactory(self.logger, config.source).connect()
        
    def load(self, user):
        """
        Build a dict like:
                {'permissions'  : {role: [sites/groups]},
                'fullname'  : user.fullname,
                'dn'  : user.dn}
        """
        grpsql = """select contact.forename || ' ' ||  contact.SURNAME as fullname, 
        contact.dn, role.title, user_group.name
        from contact, role, group_responsibility, user_group
        
        where contact.username=:username
        and contact.id = group_responsibility.contact
        and group_responsibility.role = role.id
        and user_group.id = group_responsibility.user_group"""
        
        sitesql = """select contact.forename || ' ' ||  contact.SURNAME as fullname, 
        contact.dn, role.title, siteinfo_v2.cms_name
        from contact, role, site_responsibility, siteinfo_v2
        
        where contact.username=:username
        and contact.id = site_responsibility.contact
        and site_responsibility.role = role.id
        and siteinfo_v2.id = site_responsibility.site"""
        
        userdict = {}
        data = self.conn.processData([grpsql, sitesql], binds = [{'username': user},
                                                                 {'username': user}])
        for d in data:
            for r in d.fetchall():
                if 'fullname' not in userdict.keys():
                    userdict['fullname'] = r[0]
                if 'dn' not in userdict.keys():
                    userdict['dn'] = r[1]
                if 'permissions' not in userdict.keys():
                    userdict['permissions'] = {r[2]:[r[3]]}
                else:
                    if r[2] in userdict['permissions'].keys():
                        userdict['permissions'][r[2]].append(r[3])
                    else:
                        userdict['permissions'][r[2]] = [r[3]]
                print r
        return userdict
    
    def checkpass(self, user, password):
        sql = 'select passwd from user_passwd where username = :username'
        try:
            data = self.conn.processData(sql, binds = {'username': user})
            
            if len(data) == 1:
                encpassword = data[0].fetchone()[0]
                return encpassword == crypt(password, encpassword)
        except Exception, e:
            self.logger.info(str(e))
            return False
    
    def checkdn(self, user, dn):
        sql = "select dn from contact where username=:username"
        try:
            data = self.conn.processData(sql, binds = {'username': user})
            if len(data) == 1:
                dbdn = data[0].fetchone()[0]
                return dbdn == dn
        except Exception, e:
            self.logger.info(str(e))
            return False
        return False

    def getuserbydn(self, dn):
        return None
