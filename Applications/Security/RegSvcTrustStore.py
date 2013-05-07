#!/usr/bin/env python
"""
Talk to the RegSvc for a list of trust sources. Expect the regsvc to have a view
the returns data like:

{"total_rows":3,"offset":0,"rows":[
{"id":"661d893bcdc29226d8bb27a197820ca1","key":null,"value":"https://localdbs"},
{"id":"a5838e4bea747119143174d4cb3843a2","key":null,"value":"https://globaldbs"},
{"id":"edc585f8e89f2465f7dfbc7d3c3eea4b","key":null,"value":"http://localhost:8080"}
]}

"""
__revision__ = "$Id: RegSvcTrustStore.py,v 1.3 2009/12/03 20:07:54 metson Exp $"
__version__ = "$Revision: 1.3 $"

from TrustStore import TrustStore
from WMCore.Services.Service import Service
import logging
try:
    import json
except:
    import simplejson as json

class RegSvcTrustStore(TrustStore):
    def __init__(self, config):
        TrustStore.__init__(self, config)
        
        defaultdict = {'endpoint': self.store,
                       'cacheduration': config.duration,
                       'cachepath': config.path,
                       'method': 'GET'}
        
        logging.basicConfig(level = logging.DEBUG,
                format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt = '%m-%d %H:%M',
                filename = defaultdict['cachepath'] + '/regsvc.log',
                filemode = 'w')
        defaultdict['logger'] = logging.getLogger('OIDRegSvcTrustStore')

        self.svc = Service(defaultdict)
        
    def allow(self, trust_root):
        data = json.load(self.svc.refreshCache('oid-trust'))
        trusted = [x['value'] for x in data['rows']]
        return (trust_root in trusted)