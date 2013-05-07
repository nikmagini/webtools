from sqlalchemy import *

from dataProviderBase import *
from T0Mon.utils import *
from T0Mon.analysis import *
from T0Mon.consts import *
from T0Mon.sqlManager import *

from T0Mon.globals import logger
import T0Mon.config
import datetime

### Module for classes providing data about T0 components ###

class ComponentDataProvider(TableDataProvider):
    cols = Cols([])
    flagErrorTime = datetime.timedelta( minutes=6 )

    def __init__(self):
        self.title = "Time from component's last heartbeat"
        TableDataProvider.__init__(self)
        TableDataProvider._load(self)

    def _buildQuery(self):
        comps = Tbl(TABLES.COMPONENT_HEARTBEAT, True)

        self.query ="""SELECT name,last_updated FROM """ + comps


    def _analysis(self):

        newCols = []
        values = []
        timeNow = datetime.datetime.now().replace(microsecond=0)
        
        for line in self.data:
            delta = timeNow - datetime.datetime.fromtimestamp( line[1] ).replace(microsecond=0)
            values.append( delta )
            if delta < self.flagErrorTime:
                newCols.append( Col( line[0] ) )
            else:
                newCols.append(
                    Col( """<font style="background-color:red">""" +line[0] + """</font>""" )
                    )
        self.cols = Cols( newCols )
        self.data = [values]

    def _validate(self):
        """
        Valide the correctness of params, there are none
        """
        pass
