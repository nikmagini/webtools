from TrustStore import TrustStore
from WMCore.Configuration import loadConfigurationFile

class FileTrustStore(TrustStore):
    def allow(self, trust_root):
        cfg = loadConfigurationFile(self.store)
        return (trust_root in cfg.Trusts.allowed)
