'''
Created on 16 Aug 2009

@author: metson
'''
from WMCore.WebTools.NestedModel import NestedModel
from SiteDB.REST.Validate import Validator

class Get(NestedModel):
    '''
    People: Data related to the people known to SiteDB 
    '''
    def __init__(self, config):
        '''
        Initialise the RESTModel and add some methods to it.
        '''
        NestedModel.__init__(self, config)
        
        validator = Validator({'dbi':self.dbi})
        
        self.methods = {'GET':{
                               'list': {
                                        'default':{'default_data':1234, 
                                                   'call':self.info,
                                                   'version': 1,
                                                   'args': ['username'],
                                                   'expires': 3600,
                                                   'validation': []},
                                        'dn':{'default_data':1234, 
                                               'call':self.dnUserName,
                                               'version': 1,
                                               'args': ['dn'],
                                               'expires': 3600,
                                               'validation': []},
                                        'roles':{'default_data':1234, 
                                               'call':self.roles,
                                               'version': 1,
                                               'args': ['username'],
                                               'expires': 3600,
                                               'validation': []},
                                        'groups':{'default_data':1234, 
                                               'call':self.groups,
                                               'version': 1,
                                               'args': ['username'],
                                               'expires': 3600,
                                               'validation': []}}
                               }
        }
    
    def dnUserName(self, dn):
        """
        Return the username associated to the dn
        """
        sql = 'select username from contact where dn = :dn'
        binds = {'dn': dn}
        result = self.dbi.processData(sql, binds)
        data = self.formatOneDict(result)
        return {'username':data['username'], 'dn': dn}
    
    def info(self, username=None):
        """
        Return information for a given username, to include:
            site:roles
            group:roles
            dn
            email
        Can be shortened by kwarg, e.g. ?dn will only return the DN for username
        """
        return {'info': {'username':username}}
    
    def roles(self, username=None):
        """
        Return a list of the roles username has, without group/site info
        """
        return {'roles': {'username':username}}
    
    def groups(self, username=None):
        """
        Return the groups username is in
        """
        grpsql = """select contact.forename || ' ' ||  contact.SURNAME as fullname, 
        contact.dn, role.title, user_group.name
        from contact, role, group_responsibility, user_group
        
        where contact.username='metson'
        and contact.id = group_responsibility.contact
        and group_responsibility.role = role.id
        and user_group.id = group_responsibility.user_group"""
        return {'groups': {'username':username}}
    
    def sites(self, username=None):
        
        sitesql = """select contact.forename || ' ' ||  contact.SURNAME as fullname, 
        contact.dn, role.title, siteinfo_v2.cms_name
        from contact, role, site_responsibility, siteinfo_v2
        
        where contact.username='metson'
        and contact.id = site_responsibility.contact
        and site_responsibility.role = role.id
        and siteinfo_v2.id = site_responsibility.site"""
     