from sqlalchemy import *

from dataProviderBase import *
from T0Mon.utils import *
from T0Mon.consts import *
from T0Mon.sqlManager import *

from T0Mon.globals import logger
import T0Mon.config

### Module for classes providing data about T0 files ###
###################################################################################################################################### Basic DP
class BaseDP(PagedTableDataProvider):
    cols = Cols([
        Col("Id"),
        Col("Filesize", decorator = humanFilesize),
        Col("Events"),
#        Col("Status"),            # TODO : check these columns in the database, add to the final version of this table
        Col("Dataset"),
        Col("Lfn", decorator = lambda x: textToImageAlt(x))
    ])

    def __init__(self, type, orderby = 0, asc = True, page = 0):
	self.type = type
        PagedTableDataProvider.__init__(self, orderby, asc, page)
	self.selectCond = """ """
	self.fromCond = """ """
	self.whereCond = """ """

    def _buildCountQuery(self):
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsDatasetAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetTable = Tbl(TABLES.DATASET_PATH, True)
        dataTierTable = Tbl(TABLES.DATA_TIER, True)
	
        self.countQuery = """ SELECT COUNT(DISTINCT f.id)
                                FROM """ + wmbsFileDetailsTable + """ f """ +"""
				INNER JOIN """ + wmbsDatasetAssocTable  + """ a ON (a.file_id = f.id)
                                INNER JOIN """ + datasetTable  + """ dp ON (a.dataset_path_id = dp.id)
			        INNER JOIN """ + dataTierTable + """ dt ON (dp.data_tier = dt.id) """ + self.fromCond + """
                                WHERE dt.name = '""" + self.type + """' """ + self.whereCond + """ """
       

    def _buildMainQuery(self):
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsDatasetAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetTable = Tbl(TABLES.DATASET_PATH, True)
        dataTierTable = Tbl(TABLES.DATA_TIER, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)

        if self.asc:
                order = "ASC"
        else:
                order = "DESC"
	
        self.mainQuery = """ SELECT DISTINCT f.id, f.filesize, f.events, pd.name, f.lfn""" + self.selectCond + """ 
                                FROM """ + wmbsFileDetailsTable + """ f """ + """
				INNER JOIN """ + wmbsDatasetAssocTable  + """ a ON (a.file_id = f.id)
                                INNER JOIN """ + datasetTable  + """ dp ON (a.dataset_path_id = dp.id)
			        INNER JOIN """ + primaryDatasetTable + """ pd ON (dp.primary_dataset = pd.id)
				INNER JOIN """ + dataTierTable + """ dt ON (dp.data_tier = dt.id) """  \
				+ self.fromCond + """  WHERE """ + """ dt.name = '""" + self.type + """' """   + self.whereCond + """
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order

	
class ExpressDP(PagedTableDataProvider):
    cols = Cols([
        Col("Id"),
        Col("Filesize", decorator = humanFilesize),
        Col("Events"),
#        Col("Status"),            # TODO : check these columns in the database, add to the final version of this table
        Col("Lfn", decorator = lambda x: textToImageAlt(x))
    ])

    def __init__(self, orderby = 0, asc = True, page = 0):
        PagedTableDataProvider.__init__(self, orderby, asc, page)
	self.selectCond = """ """
	self.fromCond = """ """
	self.whereCond = """ """

    def _buildCountQuery(self):
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        self.countQuery = """ SELECT COUNT(DISTINCT f.id)
                                FROM """ + wmbsFileDetailsTable + """ f """  \
				+ self.fromCond +""" WHERE """ + self.whereCond + """ """
	#print self.countQuery +" "
	

    def _buildMainQuery(self):
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        if self.asc:
                order = "ASC"
        else:
                order = "DESC"
	
        self.mainQuery = """ SELECT DISTINCT f.id, f.filesize, f.events, f.lfn""" + self.selectCond + """ 
                                FROM """ + wmbsFileDetailsTable + """ f """+ self.fromCond + """  WHERE """ +  self.whereCond + """
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order
	print self.mainQuery + " "
	
	
	
class BaseAlcaskimDP(BaseDP):
    cols = Cols([
        Col("Id"),
        Col("Filesize", decorator = humanFilesize),
        Col("Events"),
#        Col("Status"),            # TODO : check these columns in the database, add to the final version of this table
        Col("Dataset"),
        Col("Lfn", decorator = lambda x: textToImageAlt(x)),
	Col("Skim")
    ])
    
    def __init__(self, orderby = 0, asc = True, page = 0):
        BaseDP.__init__(self, 'ALCARECO', orderby, asc, page)
	self.cols["Id"].decorator = buildAlcaSkimLink
        self.title = "AlcaSkim files"

    def _analysis(self):
        for line in self.data:
            processedDatasetName = line[self.cols.getId("Skim")]
            processedDatasetSkimName = processedDatasetName.split('-')[1]
            line[self.cols.getId("Skim")] = processedDatasetSkimName
	     

#########################################################################################################################3
class StreamerDP(PagedTableDataProvider):
    cols = Cols([
        Col("Id", decorator = buildStreamerLink),
        Col("Lumi Id"),
        Col("Filesize", decorator = humanFilesize),
        Col("Events"),
        Col("Name"),
        Col("Lfn", decorator = lambda x: textToImageAlt(x))
    ])

    def __init__(self, orderby = 0, asc = True, page = 0):
	self.style=[]
        PagedTableDataProvider.__init__(self, orderby, asc, page)
        self.title = 'Streamer files'
	
	
    def getStyle(self):
	    #print "STYLE: " + " ".join(self.style) 
	    return self.style[:]
    
    def _buildCountQuery(self):
        streamerTable = Tbl(TABLES.STREAMER)

        self.countQuery = select(
            [func.count(streamerTable.c.streamer_id)],
            self.whereCond
        )

    def _buildMainQuery(self):
        streamerTable = Tbl(TABLES.STREAMER)
        streamTable = Tbl(TABLES.STREAM)

        c = (
            streamerTable.c.streamer_id,
            streamerTable.c.lumi_id,
            streamerTable.c.filesize,
            streamerTable.c.events,
            streamTable.c.name,
            streamerTable.c.lfn
        )

        if self.asc: o = c[self.orderby].asc()
        else: o = c[self.orderby].desc()

        self.mainQuery = select(
            c,
            self.whereCond,
	    from_obj = [streamerTable.
                        join(streamTable, streamerTable.c.stream_id == streamTable.c.id)]
        ).order_by(o)


####################################################################################################################################### Special DP


class BaseRepackDP(BaseDP):
    def __init__(self, orderby = 0, asc = True, page = 0):
        BaseDP.__init__(self, 'RAW', orderby, asc, page)
        self.title = "Repacked files"
	self.cols["Id"].decorator = buildRepackLink

class BaseExpressDP(ExpressDP):
    def __init__(self, orderby = 0, asc = True, page = 0):
        ExpressDP.__init__(self, orderby, asc, page)
        self.title = "Express files"
	self.cols["Id"].decorator = buildExpressLink


class BaseRepackMergeDP(BaseRepackDP):
    def __init__(self, orderby = 0, asc = True, page = 0):
        BaseRepackDP.__init__(self, orderby, asc, page)
        self.title = "Repacked files"
	self.cols["Id"].decorator = buildRepackMergeLink

class BaseExpressMergeDP(BaseExpressDP):
    def __init__(self, orderby = 0, asc = True, page = 0):
        BaseExpressDP.__init__(self, orderby, asc, page)
        self.title = "Express files"
	self.cols["Id"].decorator = buildExpressMergeLink

class BaseRecoDP(BaseDP):
    def __init__(self, orderby = 0, asc = True, page = 0):
        BaseDP.__init__(self, 'RECO', orderby, asc, page)
        self.title = "Reco files"
	self.cols["Id"].decorator = buildRecoLink
################################################################################################################# Streamer
class StreamerByRunIdDP(StreamerDP):
    def __init__(self, runid, orderby = 0, asc = True, page = 0):
        StreamerDP.__init__(self, orderby, asc, page)
        streamerTable = Tbl(TABLES.STREAMER)
        self.whereCond = (streamerTable.c.run_id == runid)
        StreamerDP._load(self)

class StreamerByIdsDP(StreamerDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        StreamerDP.__init__(self, orderby, asc, page)
        streamerTable = Tbl(TABLES.STREAMER)
        self.whereCond = (streamerTable.c.streamer_id.in_(ids))
        StreamerDP._load(self)
	
	############## choose the style
	
	self.expressQuery= """ SELECT
 				count(distinct s.streamer_id)
 				from 
 				streamer s
 				INNER JOIN run_stream_style_assoc rssa ON (rssa.stream_id = s.stream_id) 
 				where s.streamer_id = """+ str(ids[0])+""" AND rssa.style_id = (SELECT id FROM PROCESSING_STYLE WHERE name = 'Express' )"""
	self.bulkQuery= """ SELECT
 				count(distinct s.streamer_id)
 				from 
 				streamer s
 				INNER JOIN run_stream_style_assoc rssa ON (rssa.stream_id = s.stream_id) 
 				where s.streamer_id = """+ str(ids[0])+""" AND rssa.style_id = (SELECT id FROM PROCESSING_STYLE WHERE name = 'Bulk' )"""
	sqlResult = executeQuery(self.expressQuery)
        self.expressCount = int(sqlResult.fetchone()[0])
        sqlResult.close()
	sqlResult = executeQuery(self.bulkQuery)
        self.bulkCount = int(sqlResult.fetchone()[0])
        sqlResult.close()
	if self.bulkCount > 0: 
	  self.style.append('Bulk')
	if self.expressCount > 0: 
	  self.style.append('Express')
	#print "STYLE  express "+ str(self.expressCount)
	#print "STYLE  bulk "+ str(self.bulkCount)

   

class StreamerByRepackJobIdsDP(StreamerDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        StreamerDP.__init__(self, orderby, asc, page)
        streamerTable = Tbl(TABLES.STREAMER)
        assocTable = Tbl(TABLES.JOB_DATASET_STREAMER_ASSOC)
        self.whereCond = streamerTable.c.streamer_id.in_(
            select([func.distinct(assocTable.c.streamer_id)], assocTable.c.job_id.in_(ids))
        )
        StreamerDP._load(self)

class StreamerByExpressJobIdsDP(StreamerDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        StreamerDP.__init__(self, orderby, asc, page)
        streamerTable = Tbl(TABLES.STREAMER)
        assocTable = Tbl(TABLES.EXPRESS_JOB_STREAMER_ASSOC)
        self.whereCond = streamerTable.c.streamer_id.in_(
            select([func.distinct(assocTable.c.streamer_id)], assocTable.c.job_id.in_(ids))
        )
        StreamerDP._load(self)
	
class StreamerByExpressIdsDP(StreamerDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        StreamerDP.__init__(self, orderby, asc, page)
        streamerTable = Tbl(TABLES.STREAMER)
        assocTable = Tbl(TABLES.REPACK_STREAMER_ASSOC)
        self.whereCond = streamerTable.c.streamer_id.in_(
            select([func.distinct(assocTable.c.streamer_id)], assocTable.c.repacked_id.in_(ids))
        )
        StreamerDP._load(self)
########################################################################################################################################### Express

class ExpressByStreamerIdsDP(BaseExpressDP): 
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseExpressDP.__init__(self, orderby, asc, page)
	self.title = "Temporary Express files"

	repackStreamerAssocTable = Tbl(TABLES.REPACK_STREAMER_ASSOC, True)

	ids_str = ""
	numIds = len(ids)
	if numIds != 0:
		if numIds > 1:
			for i in range(numIds-1):
				ids_str += str(ids[i]) + ", "
		ids_str += str(ids[-1])

        self.whereCond = """ a.streamer_id IN (""" + ids_str + """) """
	
	self.fromCond = """ INNER JOIN """ + repackStreamerAssocTable + """ a ON (a.repacked_id = f.id) """

	if numIds != 0:
	        BaseExpressDP._load(self)
		
		

class ExpressByExpressMergeIdsDP(BaseExpressDP): 
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseExpressDP.__init__(self, orderby, asc, page)
	self.title = "Temporary Express files"

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        self.whereCond = """ fs.name = 'ExpressMergeable' and fp.child IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
                            INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.parent) """

        if len(ids) != 0:
            BaseExpressDP._load(self)
	    	
class ExpressByExpressMergeJobIdsDP(BaseExpressDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseExpressDP.__init__(self, orderby, asc, page)
        self.title = "Temporary Express files"

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)

        self.whereCond = """  ja.job IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsJobAssocTable + """ ja ON (ja.fileid = f.id) """

        if numIds != 0:
                BaseExpressDP._load(self)
		
		
	    
class ExpressMergeByExpressIdsDP(BaseExpressMergeDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseExpressMergeDP.__init__(self, orderby, asc, page)

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
	wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        self.whereCond = """  fs.name = 'ExpressDBSUploadable' and fp.parent IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
			    INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.child) """

        if len(ids) != 0:
            BaseExpressMergeDP._load(self)
	    
class ExpressMergeByIdsDP(BaseExpressMergeDP):
   def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseExpressMergeDP.__init__(self, orderby, asc, page)
	ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)

        self.whereCond = """  f.id IN (""" + ids_str + """) and fs.name = 'ExpressDBSUploadable' """

        self.fromCond = """ INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
	                    INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
            	            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset) """
	
        BaseExpressMergeDP._load(self)
	
	

class ExpressByIdsDP(BaseExpressDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseExpressDP.__init__(self, orderby, asc, page)
        self.title = "Temporary Express files"

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        self.whereCond = """ fs.name = 'ExpressMergeable' and f.id IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset) """

        BaseExpressDP._load(self)
	#print self.mainQuery





class ExpressFileByRunDP(BaseExpressDP):
    def __init__(self, runid, orderby = 0, asc = True, page = 0):
        BaseExpressDP.__init__(self, orderby, asc, page)
        self.title = "Temporary Express files"
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)

	self.whereCond = """  fsf.fileset = (select """ + wmbsFilesetTable+""".id  
                                    from  """ + wmbsFilesetTable+""" where """+ wmbsFilesetTable+""".name ='ExpressMergeable' ) and 
				    f.id in  ( select """ +wmbsFileRunlumiMapTable+""".fileid from """+ \
				    wmbsFileRunlumiMapTable+""" where """+ wmbsFileRunlumiMapTable+""".run="""+str(runid)+""")"""

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid) """
        BaseExpressDP._load(self)
	#print self.mainQuery

class ExpressMergeFileByRunDP(BaseExpressDP):
    def __init__(self, runid, orderby = 0, asc = True, page = 0):
        BaseExpressDP.__init__(self, orderby, asc, page)
	self.cols["Id"].decorator = buildExpressMergeLink
        self.title = "Express files"

        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
	
	self.whereCond = """  fsf.fileset = (select """ + wmbsFilesetTable+""".id  
                                    from  """ + wmbsFilesetTable+""" where """+ wmbsFilesetTable+""".name ='ExpressDBSUploadable' ) and 
				    f.id in  ( select """ +wmbsFileRunlumiMapTable+""".fileid from """+ \
				    wmbsFileRunlumiMapTable+""" where """+ wmbsFileRunlumiMapTable+""".run="""+str(runid)+""")"""

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid) """
	#self.whereCond = """  m.run = """ + str(runid) + """ and fs.name ='ExpressDBSUploadable' """

        #self.fromCond = """ INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                            #INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            #INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset) """
        BaseExpressDP._load(self)

########################################################################################################################################### Repack
class RepackByIdsDP(BaseRepackDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseRepackDP.__init__(self, orderby, asc, page)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)

	self.whereCond = """ and fs.name = 'Mergeable' and f.id IN (""" + ids_str + """)"""

        self.fromCond = """ INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                            INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset) """

        if numIds != 0:
                BaseRepackDP._load(self)

class RepackByRunIdDP(BaseRepackDP):
    def __init__(self, runid, orderby = 0, asc = True, page = 0):
        BaseRepackDP.__init__(self, orderby, asc, page)
        self.title = "Temporary Repacked files"

        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
	wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
	wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)

	self.whereCond = """ and m.run = """ + str(runid) + """ and fs.name = 'Mergeable' """
	
	self.fromCond = """ INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid) 
			    INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
			    INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset) """

        BaseRepackDP._load(self)

class RepackByRepackMergeIdsDP(BaseRepackDP): 
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseRepackDP.__init__(self, orderby, asc, page)
	self.title = "Temporary Repacked files"

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        self.whereCond = """ and fs.name = 'Mergeable' and fp.child IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
                            INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.parent) """

        if len(ids) != 0:
            BaseRepackDP._load(self)
	    
	    

class RepackByRepackMergeJobIdsDP(BaseRepackDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseRepackDP.__init__(self, orderby, asc, page)
        self.title = "Temporary Repacked files"

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)

        self.whereCond = """ and ja.job IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsJobAssocTable + """ ja ON (ja.fileid = f.id) """

        if numIds != 0:
                BaseRepackDP._load(self)


class RepackByStreamerIdsDP(BaseRepackDP): 
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseRepackDP.__init__(self, orderby, asc, page)
	self.title = "Temporary Repacked files"

	repackStreamerAssocTable = Tbl(TABLES.REPACK_STREAMER_ASSOC, True)

	ids_str = ""
	numIds = len(ids)
	if numIds != 0:
		if numIds > 1:
			for i in range(numIds-1):
				ids_str += str(ids[i]) + ", "
		ids_str += str(ids[-1])

        self.whereCond = """ and a.streamer_id IN (""" + ids_str + """) """
	
	self.fromCond = """ INNER JOIN """ + repackStreamerAssocTable + """ a ON (a.repacked_id = f.id) """

	if numIds != 0:
	        BaseRepackDP._load(self)
######################################################################################################################## RepackMerge

class RepackMergeByRecoIdsDP(BaseRepackMergeDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseRepackMergeDP.__init__(self, orderby, asc, page)

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        self.whereCond = """ and fs.name = 'DBSUploadable' and fp.child IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
                            INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.parent) """

        if len(ids) != 0:
	        BaseRepackMergeDP._load(self)



class RepackMergeByExpressIdsDP(BaseRepackMergeDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseRepackMergeDP.__init__(self, orderby, asc, page)

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        self.whereCond = """ and fs.name = 'ExpressDBSUploadable' and fp.child IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
                            INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.parent) """

        if len(ids) != 0:
	        BaseRepackMergeDP._load(self)

class RepackMergeByRecoJobIdsDP(BaseRepackMergeDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseRepackMergeDP.__init__(self, orderby, asc, page)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)

        self.whereCond = """ and fs.name = 'DBSUploadable' and ja.job IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
			    INNER JOIN """ + wmbsJobAssocTable + """ ja ON (ja.fileid = f.id) """

        if numIds != 0:
                BaseRepackDP._load(self)

	
	
	
class RepackMergeByIdsDP(BaseRepackMergeDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseRepackMergeDP.__init__(self, orderby, asc, page)

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        self.whereCond = """ and fs.name = 'DBSUploadable' and f.id IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset) """

        BaseRepackMergeDP._load(self)

class RepackMergeByRepackMergeJobIdsDP(BaseRepackMergeDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseRepackMergeDP.__init__(self, orderby, asc, page)
        repackedTable = Tbl(TABLES.REPACKED)
        assocTable = Tbl(TABLES.MERGE_JOB_REPACK_ASSOC)
        parentageTable = Tbl(TABLES.REPACKED_MERGE_PARENTAGE)
        self.whereCond = repackedTable.c.repacked_id.in_(
            select([parentageTable.c.output_id], parentageTable.c.input_id.in_(
                select([assocTable.c.repacked_id], assocTable.c.job_id.in_(ids))
            ))
        )
        BaseRepackMergeDP._load(self)

class RepackMergeByRepackIdsDP(BaseRepackMergeDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseRepackMergeDP.__init__(self, orderby, asc, page)

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
	wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        self.whereCond = """ and fs.name = 'DBSUploadable' and fp.parent IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
			    INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.child) """

        if len(ids) != 0:
            BaseRepackMergeDP._load(self)
	    
	    
class RepackMergeByRunIdDP(BaseRepackMergeDP):
    def __init__(self, runid, orderby = 0, asc = True, page = 0):
        BaseRepackMergeDP.__init__(self, orderby, asc, page)

        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)

        self.whereCond = """ and m.run = """ + str(runid) + """ and fs.name = 'DBSUploadable' """

        self.fromCond = """ INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
	                    INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
            	            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset) """

        BaseRepackMergeDP._load(self)

####################################################################################################################################### Reco




class RecoMergeByRunIdDP(BaseRecoDP):
        def __init__(self, runid, orderby = 0, asc = True, page = 0):
                BaseRecoDP.__init__(self, orderby, asc, page)
		self.title = "Reco Merge files"
		self.cols["Id"].decorator = buildRecoMergeLink

                wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
                wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
                wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)

                self.whereCond = """ and m.run = """ + str(runid) + """ and fs.name = 'DBSUploadable' """

                self.fromCond = """ INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
		                    INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
			            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset) """

                BaseRecoDP._load(self)

class RecoMergeByIdsDP(BaseRecoDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseRecoDP.__init__(self, orderby, asc, page)
	self.title = "Reco Merge files"
	self.cols["Id"].decorator = buildRecoMergeLink

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        self.whereCond = """ and fs.name = 'DBSUploadable' and f.id IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset) """

        BaseRecoDP._load(self)


class RecoMergeByRecoIdsDP(BaseRecoDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseRecoDP.__init__(self, orderby, asc, page)
	self.title = "Reco Merge files"
	self.cols["Id"].decorator = buildRecoMergeLink

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        self.whereCond = """ and fs.name = 'DBSUploadable' and fp.parent IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
                            INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.child) """

        if len(ids) != 0:
            BaseRecoDP._load(self)

class RecoMergeByAlcaSkimJobIdsDP(BaseRecoDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseRecoDP.__init__(self, orderby, asc, page)
	self.title = "Reco Merge files"
        self.cols["Id"].decorator = buildRecoMergeLink

        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        self.whereCond = """ and fs.name = 'DBSUploadable' and ja.job IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
                            INNER JOIN """ + wmbsJobAssocTable + """ ja ON (ja.fileid = f.id) """

        if len(ids) != 0:
            BaseRecoDP._load(self)

class RecoMergeByAlcaSkimIdsDP(BaseRecoDP): 
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseRecoDP.__init__(self, orderby, asc, page)
	self.title = "Reco Merge files"
	self.cols["Id"].decorator = buildRecoMergeLink

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        self.whereCond = """ and fs.name = 'DBSUploadable' and fp.child IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
                            INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.parent) """

        if len(ids) != 0:
            BaseRecoDP._load(self)

############################################################################################################################################### Alca



class AlcaskimByRunIdDP(BaseAlcaskimDP):
        def __init__(self, runid, orderby = 0, asc = True, page = 0):
                BaseAlcaskimDP.__init__(self, orderby, asc, page)
	        self.title = "Temporary AlcaSkim files"

	        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
        	wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
	        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
                processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)

		self.selectCond = """, proc.name as skim"""

        	self.whereCond = """ and m.run = """ + str(runid) + """ and fs.name = 'Mergeable' """

	        self.fromCond = """ INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
        	                    INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                	            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
				    INNER JOIN """ + processedDatasetTable + """ proc ON (dp.processed_dataset = proc.id) """

                BaseAlcaskimDP._load(self)


class AlcaskimMergeByRunIdDP(BaseAlcaskimDP):
        def __init__(self, runid, orderby = 0, asc = True, page = 0):
                BaseAlcaskimDP.__init__(self, orderby, asc, page)
		self.cols["Id"].decorator = buildAlcaSkimMergeLink
                self.title = "AlcaSkim files"

                wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
                wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
                wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
                processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)

		self.selectCond = """, pds.name as skim"""

		self.whereCond = """ and m.run = """ + str(runid) + """ and fs.name = 'DBSUploadable' """

                self.fromCond = """ INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                                    INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                                    INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset) 
				    INNER JOIN """ + processedDatasetTable + """ pds ON (dp.processed_dataset = pds.id) """

                BaseAlcaskimDP._load(self)


class AlcaSkimByIdsDP(BaseAlcaskimDP):
        def __init__(self, ids, orderby = 0, asc = True, page = 0):
                BaseAlcaskimDP.__init__(self, orderby, asc, page)
                self.title = "Temporary AlcaSkim files"

	        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        	wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
                processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)
	
	        ids_str = ""
	        numIds = len(ids)
	        if numIds != 0:
	                if numIds > 1:
	                        for i in range(numIds-1):
	                                ids_str += str(ids[i]) + ", "
	                ids_str += str(ids[-1])

		self.selectCond = """, pds.name as skim"""
	
	        self.whereCond = """ and fs.name = 'Mergeable' and f.id IN (""" + ids_str + """) """
	
                self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                                    INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
                                    INNER JOIN """ + processedDatasetTable + """ pds ON (dp.processed_dataset = pds.id) """
	
	        BaseAlcaskimDP._load(self)



class AlcaSkimByRecoMergeIdsDp(BaseAlcaskimDP):
        def __init__(self, ids, orderby = 0, asc = True, page = 0):
                BaseAlcaskimDP.__init__(self, orderby, asc, page)
                self.title = "Temporary AlcaSkim files"

	        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
	        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
	        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)
                processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)

	        ids_str = ""
	        numIds = len(ids)
	        if numIds != 0:
	                if numIds > 1:
	                        for i in range(numIds-1):
	                                ids_str += str(ids[i]) + ", "
	                ids_str += str(ids[-1])

                self.selectCond = """, pds.name as skim"""

	        self.whereCond = """ and fs.name = 'Mergeable' and fp.parent IN (""" + ids_str + """) """
	
	        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
	                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
	                            INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.child) 
				    INNER JOIN """ + processedDatasetTable + """ pds ON (dp.processed_dataset = pds.id) """
	
	        if len(ids) != 0:
	        	BaseAlcaskimDP._load(self)


class AlcaSkimByAlcaSkimMergeJobIdsDP(BaseAlcaskimDP):
	def __init__(self, ids, orderby = 0, asc = True, page = 0):
        	BaseAlcaskimDP.__init__(self, orderby, asc, page)
	        self.title = "Temporary AlcaSkim files"
	
	        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
	        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
	        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
                processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)

	        ids_str = ""
	        numIds = len(ids)
	        if numIds != 0:
	                if numIds > 1:
	                        for i in range(numIds-1):
	                                ids_str += str(ids[i]) + ", "
	                ids_str += str(ids[-1])

                self.selectCond = """, pds.name as skim"""
	
	        self.whereCond = """ and fs.name = 'Mergeable' and ja.job IN (""" + ids_str + """) """
	
	        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
	                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
	                            INNER JOIN """ + wmbsJobAssocTable + """ ja ON (ja.fileid = f.id) 
				    INNER JOIN """ + processedDatasetTable + """ pds ON (dp.processed_dataset = pds.id) """
	
	        if len(ids) != 0:
	        	BaseAlcaskimDP._load(self)


class AlcaSkimMergeByAlcaSkimIdsDP(BaseAlcaskimDP):
        def __init__(self, ids, orderby = 0, asc = True, page = 0):
                BaseAlcaskimDP.__init__(self, orderby, asc, page)
		self.cols["Id"].decorator = buildAlcaSkimMergeLink

                wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
                wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
                wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)
                processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)

                ids_str = ""
                numIds = len(ids)
                if numIds != 0:
                        if numIds > 1:
                                for i in range(numIds-1):
                                        ids_str += str(ids[i]) + ", "
                        ids_str += str(ids[-1])

                self.selectCond = """, pds.name as skim"""

                self.whereCond = """ and fs.name = 'DBSUploadable' and fp.parent IN (""" + ids_str + """) """

                self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                                    INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
                                    INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.child)
                                    INNER JOIN """ + processedDatasetTable + """ pds ON (dp.processed_dataset = pds.id) """

                if len(ids) != 0:
                        BaseAlcaskimDP._load(self)


class AlcaSkimMergeByIdsDP(BaseAlcaskimDP):
        def __init__(self, ids, orderby = 0, asc = True, page = 0):
                BaseAlcaskimDP.__init__(self, orderby, asc, page)
		self.cols["Id"].decorator = buildAlcaSkimMergeLink

                wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
                wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
                processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)

                ids_str = ""
                numIds = len(ids)
                if numIds != 0:
                        if numIds > 1:
                                for i in range(numIds-1):
                                        ids_str += str(ids[i]) + ", "
                        ids_str += str(ids[-1])

                self.selectCond = """, pds.name as skim"""

                self.whereCond = """ and fs.name = 'DBSUploadable' and f.id IN (""" + ids_str + """) """

                self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                                    INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
                                    INNER JOIN """ + processedDatasetTable + """ pds ON (dp.processed_dataset = pds.id) """

                BaseAlcaskimDP._load(self)


class AlcaSkimByAlcaSkimMergeIdsDP(BaseAlcaskimDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseAlcaskimDP.__init__(self, orderby, asc, page)
        self.title = "Temporary AlcaSkim files"

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)
	processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

	self.selectCond = """, pds.name as skim"""

        self.whereCond = """ and fs.name = 'Mergeable' and fp.child IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
                            INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.parent) 
			    INNER JOIN """ + processedDatasetTable + """ pds ON (dp.processed_dataset = pds.id) """

        if len(ids) != 0:
            BaseAlcaskimDP._load(self)
	    
	    
class AlcaSkimByAlcaSkimMergeJobIdsDP(BaseAlcaskimDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        BaseAlcaskimDP.__init__(self, orderby, asc, page)
        self.title = "Temporary AlcaSkim files"

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)
	processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)
	wmbsJobAssoc = Tbl(TABLES.WMBS_JOB_ASSOC, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

	self.selectCond = """, pds.name as skim"""

        self.whereCond = """ and ja.job IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
                            INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.parent) 
			    INNER JOIN """ + processedDatasetTable + """ pds ON (dp.processed_dataset = pds.id) 
			     INNER JOIN """ + wmbsJobAssoc + """ ja ON (ja.fileid = f.id) """

        if len(ids) != 0:
            BaseAlcaskimDP._load(self)
################################################################################################################################## Reco Temp --new version
class RecoTempDP(PagedTableDataProvider):
    cols = Cols([
        Col("Id",decorator = buildRecoLink),
        Col("Filesize", decorator = humanFilesize),
        Col("Events"),
        Col("Tier"),
        Col("Dataset"),
        Col("Lfn", decorator = lambda x: textToImageAlt(x))
    ])

    def __init__(self, orderby = 0, asc = True, page = 0):
        PagedTableDataProvider.__init__(self, orderby, asc, page)
	self.selectCond = """ """
	self.fromCond = """ """
	self.whereCond = """ """
	#self.type = 'Reco'

    def _buildCountQuery(self):
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsDatasetAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetTable = Tbl(TABLES.DATASET_PATH, True)
        dataTierTable = Tbl(TABLES.DATA_TIER, True)
	
        self.countQuery = """ SELECT COUNT(DISTINCT f.id)
                                FROM """ + wmbsFileDetailsTable + """ f """ +"""
				INNER JOIN """ + wmbsDatasetAssocTable  + """ a ON (a.file_id = f.id)
                                INNER JOIN """ + datasetTable  + """ dp ON (a.dataset_path_id = dp.id)
			        INNER JOIN """ + dataTierTable + """ dt ON (dp.data_tier = dt.id) """ + self.fromCond + """
                                WHERE """+self.whereCond + """ """
        #print self.countQuery

    def _buildMainQuery(self):
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsDatasetAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetTable = Tbl(TABLES.DATASET_PATH, True)
        dataTierTable = Tbl(TABLES.DATA_TIER, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)

        if self.asc:
                order = "ASC"
        else:
                order = "DESC"
	 #SELECT DISTINCT f.id, f.filesize, f.events, dt.name, pd.name, f.lfn ------dp.data_tier
        self.mainQuery = """ SELECT DISTINCT f.id, f.filesize, f.events, dt.name as tier, pd.name, f.lfn
                                FROM """ + wmbsFileDetailsTable + """ f """ + """
				INNER JOIN """ + wmbsDatasetAssocTable  + """ a ON (a.file_id = f.id)
                                INNER JOIN """ + datasetTable  + """ dp ON (a.dataset_path_id = dp.id)
			        INNER JOIN """ + primaryDatasetTable + """ pd ON (dp.primary_dataset = pd.id)
				INNER JOIN """ + dataTierTable + """ dt ON (dp.data_tier = dt.id) """  \
				+ self.fromCond + """  WHERE """ + self.whereCond + """
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order
	#print self.mainQuery
	

class RecoByRunIdDP(RecoTempDP):
    def __init__(self, runid, orderby = 0, asc = True, page = 0):
        RecoTempDP.__init__(self, orderby, asc, page)
        self.title = "Temporary Reco files"

        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
	self.whereCond = """ ((dt.name='RECO' and fs.name = 'Mergeable')  or
			     (dt.name='ALCARECO' and fs.name = 'AlcaSkimmable')) and m.run = """ + str(runid) 

        #self.whereCond = """  + """ and fs.name = 'Mergeable' """

        self.fromCond = """ INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                            INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset) """

        RecoTempDP._load(self)

class RecoByRecoMergeJobIdsDP(RecoTempDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        RecoTempDP.__init__(self, orderby, asc, page)
        self.title = "Temporary Reco files"

        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])
        self.whereCond = """ ((dt.name='RECO' and fs.name = 'Mergeable')  or
			     (dt.name='ALCARECO' and fs.name = 'AlcaSkimmable')) 
	                      and ja.job IN (""" + ids_str + """) """

        #self.whereCond = """ and fs.name = 'Mergeable' and ja.job IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
			    INNER JOIN """ + wmbsJobAssocTable + """ ja ON (ja.fileid = f.id) """

        if len(ids) != 0:
            RecoTempDP._load(self)


class RecoByMergeIdsDP(RecoTempDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        RecoTempDP.__init__(self, orderby, asc, page)
        self.title = "Temporary Reco files"

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])
	self.whereCond = """ ((dt.name='RECO' and fs.name = 'Mergeable')  or
			     (dt.name='ALCARECO' and fs.name = 'AlcaSkimmable'))
	                      and fp.parent IN (""" + ids_str + """) """

        #self.whereCond = """ and fs.name = 'Mergeable' and fp.parent IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
                            INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.child) """

        if len(ids) != 0:
            RecoTempDP._load(self)			
				
class RecoByRecoMergeIdsDP(RecoTempDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        RecoTempDP.__init__(self, orderby, asc, page)
        self.title = "Temporary Reco files"
	
        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])

        self.whereCond = """ ((dt.name='RECO' and fs.name = 'Mergeable')  or
			     (dt.name='ALCARECO' and fs.name = 'AlcaSkimmable')) 
	                      and fp.child IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
                            INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.parent) """

        if len(ids) != 0:
            RecoTempDP._load(self)


class RecoByIdsDP(RecoTempDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        RecoTempDP.__init__(self, orderby, asc, page)
        self.title = "Temporary Reco files"

        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
        #wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)
        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])
	self.whereCond = """ ((dt.name='RECO' and fs.name = 'Mergeable')  or
			     (dt.name='ALCARECO' and fs.name = 'AlcaSkimmable')) 
	                      and f.id IN (""" + ids_str + """) """


        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)""" 
			    #INNER JOIN """ + wmbsFileParentTable + """ fp ON (f.id = fp.parent) """

        RecoTempDP._load(self)


class RecoByAlcaSkimJobIdsDP(RecoTempDP):
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        RecoTempDP.__init__(self, orderby, asc, page)
        self.title = "Temporary Reco files"

        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)

        ids_str = ""
        numIds = len(ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                ids_str += str(ids[i]) + ", "
                ids_str += str(ids[-1])
        self.whereCond = """  (dt.name='ALCARECO' and fs.name = 'AlcaSkimmable') 
	                      and ja.job IN (""" + ids_str + """) """

        #self.whereCond = """ and fs.name = 'Mergeable' and ja.job IN (""" + ids_str + """) """

        self.fromCond = """ INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
			    INNER JOIN """ + wmbsJobAssocTable + """ ja ON (ja.fileid = f.id) """

        if len(ids) != 0:
            RecoTempDP._load(self)
