from Framework.Context import Context
from Tools.SecurityModuleCore import SecurityTokenFactory, DummySecurityTokenImpl, SecurityToken

context = Context ()
context.addService (SecurityTokenFactory (context, DummySecurityTokenImpl))

token = SecurityToken ()
assert (token.dn, "admin")
assert (token.userId, 0)