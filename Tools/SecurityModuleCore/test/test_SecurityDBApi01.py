from Framework import Context
from Framework.Logger import Logger

from Crypto.Cipher import Blowfish
from base64 import b64encode, b64decode
import crypt

import time, calendar, datetime

from Tools.SecurityModuleCore.SecurityDBApi import SecurityDBApi
print "**** Security Module tests ****"
context = Context ()
context.addService (Logger ("securitymoduletest"))
api = SecurityDBApi (context)

context.Logger().message("Test roles:")
context.Logger().message("    swakef as prod operator: %s" % api.hasGroupResponsibility ("swakef", "production", "Production Operator"))
context.Logger().message("    metson as RAL DM: %s" % api.hasSiteResponsibility ("metson", "RAL", "Data Manager"))
context.Logger().message("    metson as site 1 Site Admin: %s" % api.hasSiteResponsibility ("metson", "1", "Site Admin"))

context.Logger().message("hasGroup:")
context.Logger().message("    swakef as member of production group: %s" % api.hasGroup ("swakef", "production"))
context.Logger().message("    metson as member of production group: %s" % api.hasGroup ("metson", "production"))
context.Logger().message("    metson as member of global group: %s" % api.hasGroup ("metson", "global"))

context.Logger().message("hasSite:")
context.Logger().message("    swakef as associated to RAL: %s" % api.hasSite ("swakef", "RAL"))
context.Logger().message("    metson as associated to RAL: %s" % api.hasSite("metson", "RAL"))
context.Logger().message("    metson as associated to site 1: %s" % api.hasSite("metson", "1"))

context.Logger().message("hasResponsibility:")
context.Logger().message("    swakef as a Data Manager: %s" % api.hasRole ("swakef", "Data Manager"))
context.Logger().message("    metson as a Data Manager: %s" % api.hasRole ("metson", "Data Manager"))

context.Logger().message("xForN")
context.Logger().message("    swakef has Prod. Op. role for following groups: %s" % api.groupsForRole("swakef", "Production Operator"))
context.Logger().message("    swakef has the following roles for group 'production': %s" % api.rolesForGroup("swakef", "production"))
context.Logger().message("    metson has Data Manager role for following sites: %s" % api.sitesForRole("metson", "Data Manager"))
context.Logger().message("    metson has the following roles for site 'RAL': %s" % api.rolesForSite("metson", "RAL"))
context.Logger().message("    metson has the following roles for site 1: %s" % api.rolesForSite("metson", "1"))
context.Logger().message("Test encryption stuff:")
context.Logger().message("    Crypt key: %s" % api.getCryptoKey(1))

context.Logger().message("Admin password is: " + crypt.crypt ("admin", "fo"))
 
context.Logger().message("Password for metson is: %s" % api.getPasswordFromUsername ("metson"))
 
 
key = "MyFakeKey" + str(datetime.datetime.now()).replace(" ","")
context.Logger().message("    New key : %s" % key)
new_id = api.addCryptoKey(key)
context.Logger().message("    ID of new key: %s" % new_id)
context.Logger().message("    Check new crypt key: %s" % api.getCryptoKey(new_id))
context.Logger().message("         timestamp: %s" % api.getCryptoKey(new_id)['timestamp'])
context.Logger().message("               key: %s" % api.getCryptoKey(new_id)['key'])
#Encrypt and decrypt a string
context.Logger().message("-----------------------------------")
context.Logger().message("add an encrypt/decrypt test here!!!")

#context.Logger().message("Test getAllUsers")
#print api.getAllUserIds()
#print api.getAllUsernames()
