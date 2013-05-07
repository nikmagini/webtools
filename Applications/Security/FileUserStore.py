from UserStore import UserStore
from WMCore.Configuration import loadConfigurationFile
from crypt import crypt

class FileUserStore(UserStore):
    def load(self, user):
        cfg = loadConfigurationFile(self.store)
        user = cfg.Users.section_(user)
        # Cannot pass non str objects since the openid library does a call
        # for object.encode('UTF-8') when preparing the response to send
        return {'permissions'  : user.permissions.dictionary_(),
                'fullname'  : user.fullname,
                'dn'  : user.dn
                }
   
    def checkpass(self, username, password):
        """
        is the password correct for username
        """
        cfg = loadConfigurationFile(self.store)
        user = cfg.Users.section_(username)
        return hasattr(user,'password') and user.password==crypt(password, 
                                                                 user.password)

    
    def checkdn(self, username, dn):
        """
        is username associated with dn?
        """
        cfg = loadConfigurationFile(self.store)
        user = cfg.Users.section_(username)
        return user and user.dn == dn # The claimed id matches the provided DN 
            
    def getuserbydn(self, dn):
        cfg = loadConfigurationFile(self.store)
        user = [sec._internal_name for sec in cfg.Users if hasattr(sec, 'dn') and sec.dn == dn]
        if len(user):
            return user[0]
        return None
