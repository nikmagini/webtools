from Framework import Context
from Framework.Logger import Logger

from Tools.SiteDBCore import SiteDBApi

context = Context ()
context.addService (Logger ("sitedbtest"))
api = SiteDBApi (context)

api.connect ()
print api.getTierList ()
