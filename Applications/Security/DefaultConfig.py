from WMCore.Configuration import Configuration
from os import environ

config = Configuration()

# This component has all the configuration of CherryPy
config.component_('Webtools')
config.Webtools.port = 8400
#config.Webtools.host = 'vocms33.cern.ch' #To open the socket in this interface

# This is the application
config.Webtools.application = 'Security'

#
# This is the config for the Security application
#
config.component_('Security')
config.Security.templates = environ['WMCORE_ROOT'] + '/src/templates/WMCore/WebTools'
config.Security.admin = 'your@email.com'
config.Security.title = 'CMS OpenID Server'
config.Security.description = 'CMS OpenID Server'
config.Security.index = 'oidserver'

# The is the URL the server should announce to users or consumers
# This is optional. Defaults to http://host:port/
#config.Security.server_url = 'https://'+config.Webtools.host+':8443/openid'
#config.Security.server_url = 'https://localhost:8443/openid'

config.Security.store = 'filestore'
config.Security.store_path = '/tmp/oidserver-store'
#config.Security.store = 'dbstore'
#config.Security.store_source = 'oracle://login:pass@hostname'

# Configure how users are identified
config.Security.section_('users_store')
# A user store can either be a database or a configuration file
config.Security.users_store.object = 'FileUserStore'
config.Security.users_store.source = 'UserConfig.py'
# A database store would look like:
#config.Security.users_store.object = 'DBUserStore'
#config.Security.users_store.source = 'sqlite://users.db'


# Configures how to determine the remote sites allowed to use this server
config.Security.section_('trust_store')
config.Security.trust_store.object = 'FileTrustStore'
config.Security.trust_store.source = 'TrustConfig.py'
# If you wanted to use the reg svc for your trust store do something like:
#config.Security.trust_store.object = 'RegSvcTrustStore'
#config.Security.trust_store.duration = 0.5
#config.Security.trust_store.source = 'http://localhost:5984/registrationservice/_design/registrationservice/_view/trustedurls'
#config.Security.trust_store.path = '/tmp/regsvc'
# Views are all pages
config.Security.section_('views')

# These are all the active pages that Root.py should instantiate 
active = config.Security.views.section_('active')
active.section_('oidserver')
# The class to load for this view/page (must be in your PYTHONPATH)
active.oidserver.object = 'OidServer'

