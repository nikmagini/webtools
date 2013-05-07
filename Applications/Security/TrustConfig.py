from WMCore.Configuration import Configuration

config = Configuration()
trusts = config.component_('Trusts')

# List of trusted servers, in this case the default docs application
trusts.allowed = ['http://localhost:8080']
