"""
A TrustStore gives the security module a way to determine which remote OpenID
based web application (also called 'consumer', or 'trust' entity) is allowed
to request user authentication/authorization through this Openid server.
"""
class TrustStore:
    def __init__(self, config):
        self.store = config.source

    def allow(self, trust_root):
        return False
