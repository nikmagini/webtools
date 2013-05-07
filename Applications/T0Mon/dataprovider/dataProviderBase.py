from sqlalchemy import *

from T0Mon.utils import *
from T0Mon.consts import *
from T0Mon.sqlManager import *

from T0Mon.globals import logger
import T0Mon.config

### Base classes used by other data provider classes ###

class Cols:
    """
    Class for table columns representation
    """
    def __init__(self, cols):
        """
        Initialize columns
        """
        self.cols = cols
        self.colsMap = {}
        for col in self.cols:
            self.colsMap[col.id] = col
           
    def __len__(self):
        """
        Get the number of columns
        """
        return len(self.cols)

    def getId(self, id):
        """
        Get column id by column index or column id by index
        """
        if type(id) == int:
            return self.cols[id].id
        else:
            for i in range(len(self.cols)):
                if self.cols[i].id == id:
                    return i
            raise Exception("Column with id " + str(id) + " not found")

    def __setitem__(self, id, col):
        """
        Set column by index or by id
        """
        if type(id) == int:
            self.cols[id] = col
        else:
            for i in range(len(self.cols)):
                if self.cols[i].id == id:
                    self.cols[i] = col
                    break
            raise Exception("Column with id " + str(id) + " not found")

    def __getitem__(self, id):
        """
        Get column by id or by index
        """
        if type(id) == int:
            return self.cols[id]
        else:
            return self.colsMap[id]

class DoubleCols:
    def __init__(self, cols):
        self.cols = cols
        self.colsMap = {}
        self.subColsMap = {}
        for i in range(0, len(self.cols)):
            self.colsMap[self.cols[i][0].id] = self.cols[i][0]
            self.subColsMap[self.cols[i][0].id] = self.cols[i][1]

    def __len__(self):
        """
        Returns the number of main columns the table has
        """
        return len(self.cols)

    def getTotalNumSubCols(self):
        """
        Returns the number of sub columns the table has
        """
        subCols = 0
        for i in range(0, len(self.cols)):
            n = len(self.cols[i][1])
            if n==0:
                subCols += 1
            else:
                subCols += n
        return subCols

    def getNumSubColsIn(self, id):
        """
        Returns the number of subcolumns that the main column with id identifier has
        """
        if type(id) == int:
            return len(self.cols[id][1])
        else:
            return len(self.subColsMap[id])
        
    def getNumMainCols(self):
        """
        Returns the number of main columns the table has
        """
        return len(self.cols)

    def __getitem__(self, id):
        """
        Returns all the set, main col with its set of sub cols
        """
        return self.cols[id]

    def getMainCol(self, id):
        """
        Returns the main col with id identifier
        """
        if type(id) == int:
            return self.cols[id][0]
        else:
            return self.colsMap[id]

    def getSubCols(self, id):
        """
        Returns the set of sub columns with id identifier
        """
        if type(id) == int:
            return self.cols[id][1]
        else:
            return self.subColsMap[id]

    def getSubCol(self, i, j):
        """
        Returns the subcolumn with i and j identifiers
        """
        if type(i) == int:
            return self.cols[i][1][j]
        else:
            return self.subColsMap[i][j]

    def getId(self, id, sub = None):
        """
        Get column id by column index or column id by index, both levels, main and subcolumns.
        """
	if sub == None:  ## Case when a main column is required
	    if type(id) == int:
            	return self.cols[id][0].id
            else:
            	for i in range(len(self.cols)):
                    if self.cols[i][0].id == id:
                    	return i
            	raise Exception("Column with id " + str(id) + " not found")
	else: ## Case when a sub column is required
	    if type(id) == int:
		if type(sub) == int:
		    return self.cols[id][1][sub].id
		else:
		    total = 0
		    for c in range(0, id):
			sucCols = self.getNumSubColsIn(c)
			if subCols == 0:
			    subCols = 1
			total += subCols
		    for i in range(len(self.cols[id][1])):
			if self.cols[id][1][i].id == sub:
			    total += i
			    return total
		    raise Exception("Column with sub " + str(sub) + " in main column with id " + str(id) + " not found")
	    else:
        	if type(sub) == int:
		    for i in range(len(self.cols)):
			if self.cols[i][0].id == id:
			    return self.cols[i][1][sub].id
		    raise Exception("Column with sub " + str(sub) + " in main column with id " + str(id) + " not found")
                else:
		    total = 0
		    for i in range(len(self.cols)):
                        if self.cols[i][0].id == id:
			    for j in range(len(self.cols[i][1])):
				if self.cols[i][1][j].id == sub:
				    total += j
	                            return total
			    raise Exception("Column with sub " + str(sub) + " in main column with id " + str(id) + " not found")
			subCols = self.getNumSubColsIn(i)
			if subCols == 0:
			    subCols = 1
			total += subCols
		    raise Exception("Column with sub " + str(sub) + " in main column with id " + str(id) + " not found")


class Col:
    """
    Class for table column representation
    """
    def __init__(self, id, title = None, decorator = None, info = None, visible = True):
        """
        Initialize column

        If title is None, title becomes the same as id
        - id            column id (must be string)
        - title         column title
        - decorator     the function used to decorate column data
        - info          help text associated with column
        - visible       is column visible?
        """
        self.id = id
        if title == None:
            self.title = self.id
        else:
            self.title = title
        self.decorator = decorator
        self.info = info
        self.visible = visible

class TableDataProvider:
    """
    Parent class for all table data providers

    TableDataProvider is an object that provides data from DB
    formatted in a table

    Public members:

    - qtime     the time main query took to execute
    - atime     the time table data analysis took
    - bindParams    parameteres that are bind with the query
    """
    def __init__(self, orderby = 0, asc = True):
        """
        Initialize TableDataProvider

        Params:
        - orderby   the index of column by which the table should be ordered
        - asc       if true ordering should be ascending, else - descending
        """
        self.orderby = orderby
        self.asc = asc
        self.bindParams = None
        self.qtime = 0
        self.data = []
        self.atime = 0

    def _load(self):
        """
        Template method for loading the object with data from DB
        """
        self._buildQuery()
        self._validate()
        self._execute()
        start = datetime.datetime.now()
        self._analysis()
        delta = datetime.datetime.now() - start
        self.atime = delta.seconds * 1000 + delta.microseconds / float(1000)

    def _analysis(self):
        """
        Analyse table data after loading it from DB
        """
        return None

    def _execute(self):
        """
        Execute main query and load data from DB
        """
        sqlResult = executeQuery(self.query, self.bindParams)
        self.data = self._sqlResultToData(sqlResult)
        self.qtime = sqlResult.time
        sqlResult.close()

    def _validate(self):
        """
        Valide the correctness of params
        """
        if (self.orderby < 0 or self.orderby >= len(self.cols)):
            globals.logger.log("Bad orderby col number provided for " + str(self))
            self.orderby = 0

    def _sqlResultToData(self, sqlResult):
        """
        Transform sql result to array
        """
        data = []
        for line in sqlResult: data.append(list(line))
        return data

class PagedTableDataProvider(TableDataProvider):
    """
    This class extends TableDataProvider and improves it with paging mechanism

    On _execute it executes two queries:
    countQuery  - for counting how much data is in DB (result is stored in dataCount)
    mainQuery   - for getting the actual page of data
    """

    def __init__(self, orderby, asc, page = None, pageSize = config.PAGE_SIZE):
        """
        Initialize PagedTableDataProvider

        Params:
        - orderby   the index of column by which the table should be ordered
        - asc       if true ordering should be ascending, else - descending
        - page      the number of page that should be displayed
        - pageSize  size of a page
        """
        TableDataProvider.__init__(self, orderby, asc)
        self.page = page
        self.pageSize = pageSize

    def _buildQuery(self):
        self._buildMainQuery()
        self._buildCountQuery()

    def _validate(self):
        TableDataProvider._validate(self)
        if self.page != None and self.page < 0:
            globals.logger.log("Bad page number provided for " + str(self))
            self.page = None

    def _execute(self):
        if self.page != None:
            # if the main query is string
            if type(self.mainQuery) == str:
                self.mainQuery = """SELECT * FROM (""" + \
                    """ SELECT
                        a.*,
                        rownum rnum
                        FROM
                        (""" + str(self.mainQuery) + """) a
                        WHERE rownum <= """ + str(int(self.page * self.pageSize + self.pageSize)) + \
                        """)
                        WHERE rnum > """ + str(int(self.page * self.pageSize))
            # if main query is sqlalchemy object
            else:
                self.mainQuery = self.mainQuery.apply_labels()
                self.mainQuery = self.mainQuery. \
                    offset(self.page * self.pageSize). \
                    limit(self.pageSize)
        # main query execution
	#print self.mainQuery
        sqlResult = executeQuery(self.mainQuery, self.bindParams)
        self.data = self._sqlResultToData(sqlResult)
        self.qtime = sqlResult.time
        sqlResult.close()
        # count query execution
        sqlResult = executeQuery(self.countQuery)
        self.dataCount = int(sqlResult.fetchone()[0])
        self.qtime += sqlResult.time
        sqlResult.close()

 
class StatsDataProvider:

    def __init__(self, title, tableName):
        self.title = title
        self.tableName = tableName
        self.qtime = 0
        self.data = []
        self.data.append([])
        self.bindParams = None

    def _buildCols(self):
        self.cols = getStatsColsRepack(self.tableName)

    def _buildQuery(self, status):
        jobTable = Tbl(self.tableName)
        self.query = select([func.count(jobTable.c.job_status)], jobTable.c.job_status == status)

    def load(self):
        self._buildCols()
        for i in range (JOB_NEW, JOB_FAILURE + 1):
            self._buildQuery(i)
            sqlResult = executeQuery(self.query, self.bindParams)
            self.data[0].append(sqlResult.fetchone()[0])
            self.qtime += sqlResult.time
            sqlResult.close()

def getStatsColsRepack(tableName, runid = None):
    return Cols([
            Col("New jobs", decorator=lambda x: formRepackJobTableLink(x, tableName, JOB_NEW, runid)),
            Col("Used jobs", decorator=lambda x: formRepackJobTableLink(x, tableName, JOB_USED, runid)),
            Col("Successful jobs", decorator=lambda x: formRepackJobTableLink(x, tableName, JOB_SUCCESS, runid)),
            Col("Failed jobs", decorator=lambda x: formRepackJobTableLink(x, tableName, JOB_FAILURE, runid)),
        ])

def getStatsColsMergeRecoAlca(inputTier, mergeFlag, runid = None):
    return Cols([
            Col("Acquired jobs", decorator=lambda x: formJobTableLink(x, inputTier, mergeFlag, "ACQUIRED", runid)),
            Col("Successful jobs", decorator=lambda x: formJobTableLink(x, inputTier, mergeFlag, "COMPLETE", runid)),
            Col("Failed jobs", decorator=lambda x: formJobTableLink(x, inputTier, mergeFlag, "FAILED", runid)),
        ])



