from WMCore.Configuration import Configuration

config = Configuration()
users = config.component_('Users')

users.section_('diego')
users.diego.fullname = 'Diego Gomes'

users.diego.section_('permissions')
users.diego.permissions.section_('Admin')
users.diego.permissions.Admin = 'T2_BR_UERJ'
users.diego.permissions.section_('Developer')
users.diego.permissions.Developer = 'CMS DMWM' 

# diego's password is password123
users.diego.password = 'abJnggxhB/yWI'
users.diego.dn = '/DC=org/DC=doegrids/OU=People/CN=Diego da Silva Gomes 849253'
                         
users.section_('simon')
users.simon.fullname = 'Simon Metson'

users.simon.section_('permissions')
users.simon.permissions.section_('Admin')
users.simon.permissions.Admin = ['T1_CH_CERN', 'T2_UK_SGrid']
users.simon.permissions.section_('L2')
users.simon.permissions.L2 = 'CMS DMWM' 

# simon's password is password
users.simon.password = 'FJxPnfhdJ5Ifc'
users.simon.dn = '/grid/cms/cern/simon'
