from sqlalchemy import *

from dataProviderBase import *
from T0Mon.utils import *
from T0Mon.consts import *
from T0Mon.sqlManager import *

from T0Mon.globals import logger
import T0Mon.config

### Module for classes providing data about T0 jobs ###

################################################################################################################################################# DATA   PROVIDERS

###########################################################################################################EXPRESS
class ExpressStatsDataProvider(StatsDataProvider):
    def __init__(self, runid, title = "Express stats"):
        StatsDataProvider.__init__(self, title, TABLES.EXPRESS_JOBS)
        self.runid = runid
        StatsDataProvider.load(self)

    def _buildCols(self):
        self.cols = getStatsColsRepack(self.tableName, self.runid)  #cols names?? what status??? see DataPRoviderBase

    def _buildQuery(self, status):
        jobTable = Tbl(self.tableName, True)
        assocTable = Tbl(TABLES.EXPRESS_JOB_STREAMER_ASSOC, True)
        streamerTable = Tbl(TABLES.STREAMER, True)
	self.query = """SELECT COUNT(*)
                          FROM (  SELECT DISTINCT j.job_id FROM """ +jobTable +""" j
			   INNER JOIN """ + assocTable + """ assoc ON (j.job_id = assoc.job_id)
			   INNER JOIN """ + streamerTable + """ stream ON (stream.streamer_id = assoc.streamer_id)
			   WHERE j.job_status ="""+ str(status) +""" AND stream.run_id =""" + str(self.runid) + """ )""" 

class ExpressGetStreamersDataProvider(PagedTableDataProvider):
    def __init__(self, orderby = 0, asc = True, page = 0, pageSize = config.PAGE_SIZE):
        PagedTableDataProvider.__init__(self, orderby, asc, page, pageSize = pageSize)
        self.title = "Express jobs"
        self.cols = Cols([
            Col("Job ID", decorator=buildExpressJobLink),
            Col("Run ID", decorator=formRunLink),
            Col("Definition time", decorator=formatTime),
            Col("Streamers"),
        ])
	
    def _buildCountQuery(self):
        jobTable = Tbl(TABLES.EXPRESS_JOBS)
        assocTable = Tbl(TABLES.EXPRESS_JOB_STREAMER_ASSOC)
        #datasetTable = Tbl(TABLES.PRIMARY_DATASET)
        streamerTable = Tbl(TABLES.STREAMER)
        self.countQuery = select(
            [func.count(func.distinct(jobTable.c.job_id))],
            self.whereCond,
            from_obj = [
                jobTable.
                join(assocTable, jobTable.c.job_id == assocTable.c.job_id).
                join(streamerTable, streamerTable.c.streamer_id == assocTable.c.streamer_id)
#                join(datasetTable, datasetTable.c.dataset_id == assocTable.c.dataset_id)
            ]
        )

    def _buildMainQuery(self):
        jobTable = Tbl(TABLES.EXPRESS_JOBS)
        assocTable = Tbl(TABLES.EXPRESS_JOB_STREAMER_ASSOC)
        statusTable = Tbl(TABLES.JOB_STATUS)
        streamerTable = Tbl(TABLES.STREAMER)
        #datasetTable = Tbl(TABLES.PRIMARY_DATASET)
	#streamTable = Tbl(TABLES.STREAM)

        c = (
             jobTable.c.job_id,
             streamerTable.c.run_id,
             jobTable.c.definition_time,
             func.count(func.distinct(assocTable.c.streamer_id)).label("num_streamers"),
             #streamTable.c.name,
             #statusTable.c.status
        )

        if self.asc: o = c[self.orderby].asc()
        else: o = c[self.orderby].desc()

        self.mainQuery = select(
            c,
            self.whereCond,
            from_obj = [
                jobTable.
                #join(statusTable, jobTable.c.job_status == statusTable.c.id).
                join(assocTable, jobTable.c.job_id == assocTable.c.job_id).
                join(streamerTable, streamerTable.c.streamer_id == assocTable.c.streamer_id)
                #join(streamTable, streamerTable.c.stream_id == streamTable.c.id)
            ]
            ).group_by(
                jobTable.c.job_id,
                jobTable.c.definition_time,
                streamerTable.c.run_id,
                #streamTable.c.name,
                #statusTable.c.status,
                
            ).order_by(o)
###########################################################################################################EXPRESS MERGE
class ExpressMergeGetFilesDataProvider(PagedTableDataProvider):

    def __init__(self, status, orderby = 0, asc = True, page = 0, pageSize = config.PAGE_SIZE):
        PagedTableDataProvider.__init__(self, orderby, asc, page, pageSize = pageSize)
        self.title = "Express Merge jobs"
        #self.status = status
        self.cols = Cols([
            Col("Job ID", decorator=buildExpressMergeJobLink),
            Col("Run ID", decorator=formRunLink),
            Col("Definition time", decorator=formatTime),
            Col("# of files") 
        ])

    def _buildCountQuery(self):
        jobTable = Tbl(TABLES.WMBS_JOB)
        jobTableState = Tbl(TABLES.WMBS_JOB_STATE)
        jobGroupTable = Tbl(TABLES.WMBS_JOBGROUP)
	#statusTable = Tbl(TABLES.JOB_STATUS)
        assocTable = Tbl(TABLES.WMBS_JOB_ASSOC)
        fileTable = Tbl(TABLES.WMBS_FILE_DETAILS)
        fileRunLumiTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP)
        if self.status == "ACQUIRED":
            jobSelection = and_( jobTable.c.state == select( [jobTableState.c.id], jobTableState.c.name == 'created' ) )
        elif self.status == "COMPLETE":
            jobSelection = and_( jobTable.c.state == select( [jobTableState.c.id], jobTableState.c.name == 'cleanout' ),
                                 jobTable.c.outcome == 1 )
            
        elif self.status == "FAILED":
            jobSelection = and_( jobTable.c.state == select( [jobTableState.c.id], jobTableState.c.name == 'cleanout' ),
                                 jobTable.c.outcome == 0 )
        else:
            print "Unknown state request: %s" % self.status
            
      
        self.countQuery = select(
            [func.count(func.distinct(jobTable.c.id))],
            and_( self.whereCond, jobSelection ),
            from_obj = [
                jobTable.
                join(jobGroupTable, jobTable.c.jobgroup == jobGroupTable.c.id).
                join(assocTable, jobTable.c.id == assocTable.c.job).
                join(fileTable, fileTable.c.id == assocTable.c.fileid).
                join(fileRunLumiTable, fileTable.c.id == fileRunLumiTable.c.fileid)
            ]
        )

    def _buildMainQuery(self):
        jobTable = Tbl(TABLES.WMBS_JOB)
        jobTableState = Tbl(TABLES.WMBS_JOB_STATE)
        jobGroupTable = Tbl(TABLES.WMBS_JOBGROUP)
        assocTable = Tbl(TABLES.WMBS_JOB_ASSOC)
        fileTable = Tbl(TABLES.WMBS_FILE_DETAILS)
        fileRunLumiTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP)
        #fileDatasetPathTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC)
        #datasetPathTable = Tbl(TABLES.DATASET_PATH)
        #datasetTable = Tbl(TABLES.PRIMARY_DATASET)
        if self.status == "ACQUIRED":
            jobSelection = and_( jobTable.c.state == select( [jobTableState.c.id], jobTableState.c.name == 'created' ) )
        elif self.status == "COMPLETE":
            jobSelection = and_( jobTable.c.state == select( [jobTableState.c.id], jobTableState.c.name == 'cleanout' ),
                                 jobTable.c.outcome == 1 )
            
        elif self.status == "FAILED":
            jobSelection = and_( jobTable.c.state == select( [jobTableState.c.id], jobTableState.c.name == 'cleanout' ),
                                 jobTable.c.outcome == 0 )
        else:
            print "Unknown state request: %s" % self.status
        

	c = (
             jobTable.c.id,
             fileRunLumiTable.c.run,
             jobTable.c.state_time,
             func.count(func.distinct(assocTable.c.fileid)).label("Input Files"),
             #datasetTable.c.name
         )

        if self.asc: o = c[self.orderby].asc()
        else: o = c[self.orderby].desc()
	

        self.mainQuery = select(
            c,
            and_(self.whereCond, jobSelection ),
            from_obj = [
                jobTable.
                join(jobGroupTable, jobTable.c.jobgroup == jobGroupTable.c.id).
                join(assocTable, jobTable.c.id == assocTable.c.job).
                join(fileTable, fileTable.c.id == assocTable.c.fileid).
                join(fileRunLumiTable, fileTable.c.id == fileRunLumiTable.c.fileid)
                #join(fileDatasetPathTable, fileTable.c.id == fileDatasetPathTable.c.file_id).
                #join(datasetPathTable, fileDatasetPathTable.c.dataset_path_id == datasetPathTable.c.id).
                #join(datasetTable, datasetTable.c.id == datasetPathTable.c.primary_dataset)
            ]
            ).group_by(
                jobTable.c.id,
                jobTable.c.state_time,
                fileRunLumiTable.c.run,
                
            ).order_by(o)
	
###########################################################################################################  REPACK

class RepackStatsDataProvider(StatsDataProvider):

	
    def __init__(self, runid, title = "Repack stats"):
        StatsDataProvider.__init__(self, title, TABLES.REPACK_JOBS)
        self.runid = runid
        StatsDataProvider.load(self)

    def _buildCols(self):
        self.cols = getStatsColsRepack(self.tableName, self.runid)

    def _buildQuery(self, status):
        jobTable = Tbl(self.tableName)
        assocTable = Tbl(TABLES.JOB_DATASET_STREAMER_ASSOC)
        streamerTable = Tbl(TABLES.STREAMER)
        self.query = select(
            [func.count(distinct(jobTable.c.job_id))],
            and_(
                jobTable.c.job_status == status,
                streamerTable.c.run_id == self.runid
            ),
            from_obj = [
                jobTable.
                join(assocTable, assocTable.c.job_id == jobTable.c.job_id).
                join(streamerTable, assocTable.c.streamer_id == streamerTable.c.streamer_id)
            ]
        )


class BaseRepackJobDP(PagedTableDataProvider):
    def __init__(self, orderby = 0, asc = True, page = 0, pageSize = config.PAGE_SIZE):
        PagedTableDataProvider.__init__(self, orderby, asc, page, pageSize = pageSize)
        self.title = "Repacker jobs"
        self.cols = Cols([
            Col("Job ID", decorator=buildRepackJobLink),
            Col("Run ID", decorator=formRunLink),
            Col("Definition time", decorator=formatTime),
            Col("Streamers"),
            Col("Stream"),
            Col("Status"),
        ])

    def _buildCountQuery(self):
        jobTable = Tbl(TABLES.REPACK_JOBS)
        assocTable = Tbl(TABLES.JOB_DATASET_STREAMER_ASSOC)
        datasetTable = Tbl(TABLES.PRIMARY_DATASET)
        streamerTable = Tbl(TABLES.STREAMER)
        self.countQuery = select(
            [func.count(func.distinct(jobTable.c.job_id))],
            self.whereCond,
            from_obj = [
                jobTable.
                join(assocTable, jobTable.c.job_id == assocTable.c.job_id).
                join(streamerTable, streamerTable.c.streamer_id == assocTable.c.streamer_id)
#                join(datasetTable, datasetTable.c.dataset_id == assocTable.c.dataset_id)
            ]
        )

    def _buildMainQuery(self):
        jobTable = Tbl(TABLES.REPACK_JOBS)
        assocTable = Tbl(TABLES.JOB_DATASET_STREAMER_ASSOC)
        statusTable = Tbl(TABLES.JOB_STATUS)
        streamerTable = Tbl(TABLES.STREAMER)
        datasetTable = Tbl(TABLES.PRIMARY_DATASET)
	streamTable = Tbl(TABLES.STREAM)

        c = (
             jobTable.c.job_id,
             streamerTable.c.run_id,
             jobTable.c.definition_time,
             func.count(func.distinct(assocTable.c.streamer_id)).label("num_streamers"),
             streamTable.c.name,
             statusTable.c.status
        )

        if self.asc: o = c[self.orderby].asc()
        else: o = c[self.orderby].desc()

        self.mainQuery = select(
            c,
            self.whereCond,
            from_obj = [
                jobTable.
                join(statusTable, jobTable.c.job_status == statusTable.c.id).
                join(assocTable, jobTable.c.job_id == assocTable.c.job_id).
                join(streamerTable, streamerTable.c.streamer_id == assocTable.c.streamer_id).
                join(streamTable, streamerTable.c.stream_id == streamTable.c.id)
            ]
            ).group_by(
                jobTable.c.job_id,
                jobTable.c.definition_time,
                streamerTable.c.run_id,
                streamTable.c.name,
                statusTable.c.status,
                
            ).order_by(o)
	    
###########################################################################################################  REPACK MERGE

class RepackMergeStatsDataProvider(StatsDataProvider):
    def __init__(self, runid, title = "Repack Merge stats"):
        StatsDataProvider.__init__(self, title, TABLES.MERGE_JOBS)
        self.runid = runid
        StatsDataProvider.load(self)

    def _buildCols(self):
        self.cols = getStatsColsMergeRecoAlca(self.tableName, self.runid)

    def _buildQuery(self, status):
        jobTable = Tbl(TABLES.MERGE_JOBS)
        assocTable = Tbl(TABLES.MERGE_JOB_REPACK_ASSOC)
        repackedTable = Tbl(TABLES.REPACKED)
        self.query = select(
            [func.count(distinct(jobTable.c.job_id))],
            and_(
                jobTable.c.job_status == status,
                repackedTable.c.run_id == self.runid
            ),
            from_obj = [
                jobTable.
                join(assocTable, assocTable.c.job_id == jobTable.c.job_id).
                join(repackedTable, assocTable.c.repacked_id == repackedTable.c.repacked_id)
            ]
        )
        # globals.logger.log(self.query)
	


class RepackMergeGetDatasetDataProvider(PagedTableDataProvider):

    def __init__(self, orderby = 0, asc = True, page = 0, pageSize = config.PAGE_SIZE):
        PagedTableDataProvider.__init__(self, orderby, asc, page, pageSize = pageSize)
        self.title = "Merge jobs"
        self.cols = Cols([
            Col("Job ID", decorator=buildRepackMergeJobLink),
            Col("Run ID", decorator=formRunLink),
            Col("Definition time", decorator=formatTime),
            Col("Repacked"),
            Col("Dataset"),
            Col("Status")
        ])

    def _buildCountQuery(self):
        jobTable = Tbl(TABLES.MERGE_JOBS)
        assocTable = Tbl(TABLES.MERGE_JOB_REPACK_ASSOC)
        repackTable = Tbl(TABLES.REPACKED)
        datasetTable = Tbl(TABLES.PRIMARY_DATASET)
        self.countQuery = select(
            [func.count(func.distinct(jobTable.c.job_id))],
            self.whereCond,
            from_obj = [
                jobTable.
                join(assocTable, jobTable.c.job_id == assocTable.c.job_id).
                join(repackTable, repackTable.c.repacked_id == assocTable.c.repacked_id).
                join(datasetTable, datasetTable.c.dataset_id == repackTable.c.dataset_id)
            ]
        )

    def _buildMainQuery(self):
        jobTable = Tbl(TABLES.MERGE_JOBS)
        statusTable = Tbl(TABLES.JOB_STATUS)
        assocTable = Tbl(TABLES.MERGE_JOB_REPACK_ASSOC)
        repackTable = Tbl(TABLES.REPACKED)
        datasetTable = Tbl(TABLES.PRIMARY_DATASET)

        c = (
            jobTable.c.job_id,
            repackTable.c.run_id,
            jobTable.c.definition_time,
            func.count(assocTable.c.repacked_id).label("num_repacked"),
            datasetTable.c.name,
            statusTable.c.status
        )

        if self.asc: o = c[self.orderby].asc()
        else: o = c[self.orderby].desc()

        self.mainQuery = select(
            c,
            self.whereCond,
            from_obj = [
                jobTable.
                join(statusTable, statusTable.c.id == jobTable.c.job_status).
                join(assocTable, jobTable.c.job_id == assocTable.c.job_id).
                join(repackTable, repackTable.c.repacked_id == assocTable.c.repacked_id).
                join(datasetTable, datasetTable.c.dataset_id == repackTable.c.dataset_id)
            ]
            ).group_by(
                jobTable.c.job_id,
                jobTable.c.definition_time,
                datasetTable.c.name,
                repackTable.c.run_id,
                statusTable.c.status,
            ).order_by(o)

######################################################################################################################     RECO

class RecoGetDatasetDataProvider(PagedTableDataProvider):

    def __init__(self, orderby = 0, asc = True, page = 0, pageSize = config.PAGE_SIZE):
        PagedTableDataProvider.__init__(self, orderby, asc, page, pageSize = pageSize)
        self.title = "Reco jobs"
        self.cols = Cols([
            Col("Job ID", decorator=buildRecoJobLink),
            Col("Run ID", decorator=formRunLink),
            Col("Definition time", decorator=formatTime),
            Col("Merged"),
            Col("Dataset"),
#            Col("Status"),     # TODO : insert again this column when I'd know the way the check the status
        ])

    def _buildCountQuery(self):
        sys.exit() #pass???
        
    def _buildMainQuery(self):
        sys.exit()



class RecoStatsDataProvider(StatsDataProvider):
    def __init__(self, runid, title = "Reco stats"):
        StatsDataProvider.__init__(self, title, TABLES.RECO_JOBS)
        self.runid = runid
        StatsDataProvider.load(self)

    def _buildCols(self):
        self.cols = getStatsCols(self.tableName, self.runid)

    def _buildQuery(self, status):
        jobTable = Tbl(TABLES.RECO_JOBS)
        assocTable = Tbl(TABLES.RECO_JOB_REPACK_ASSOC)
        repackedTable = Tbl(TABLES.REPACKED)
        self.query = select(
            [func.count(distinct(jobTable.c.job_id))],
            and_(
                jobTable.c.job_status == status,
                repackedTable.c.run_id == self.runid
            ),
            from_obj = [
                jobTable.
                join(assocTable, assocTable.c.job_id == jobTable.c.job_id).
                join(repackedTable, assocTable.c.repacked_id == repackedTable.c.repacked_id)
            ]
        )
        # globals.logger.log(self.query)
######################################################################################################################     RECO MERGE
class RecoMergeStatsDataProvider(StatsDataProvider):
    def __init__(self, runid, title = "Reco Merge stats"):
        StatsDataProvider.__init__(self, title, TABLES.MERGE_JOBS)
        self.runid = runid
        StatsDataProvider.load(self)

    def _buildCols(self):
        self.cols = getStatsCols(self.tableName, self.runid)

    def _buildQuery(self, status):
        jobTable = Tbl(self.tableName)
        assocTable = Tbl(TABLES.MERGE_JOB_RECO_ASSOC)
        recoTable = Tbl(TABLES.RECONSTRUCTED)
        self.query = select(
            [func.count(distinct(jobTable.c.job_id))],
            and_(
                jobTable.c.job_status == status,
                recoTable.c.run_id == self.runid
            ),
            from_obj = [
                jobTable.
                join(assocTable, assocTable.c.job_id == jobTable.c.job_id).
                join(recoTable, assocTable.c.reconstructed_id == recoTable.c.reconstructed_id)
            ]
        )
#################################################################################################################### ALCASKIM
class AlcaskimStatsDataProvider(StatsDataProvider):
    def __init__(self, runid, title = "AlcaSkim stats"):
        StatsDataProvider.__init__(self, title, TABLES.ALCA_JOBS)
        self.runid = runid
        StatsDataProvider.load(self)

    def _buildCols(self):
        self.cols = getStatsCols(self.tableName, self.runid)

    def _analysis(self):
        for line in self.data:
            processedDatasetName = line[self.cols.getId("Skim")]
            processedDatasetSkimName = processedDatasetName.split('-')[1]
            line[self.cols.getId("Skim")] = processedDatasetSkimName
	     

    def _buildQuery(self, status):
        jobTable = Tbl(self.tableName)
        assocTable = Tbl(TABLES.ALCA_JOB_RECO_ASSOC)
        recoTable = Tbl(TABLES.RECONSTRUCTED)
        self.query = select(
            [func.count(distinct(jobTable.c.job_id))],
            and_(
                jobTable.c.job_status == status,
                recoTable.c.run_id == self.runid
            ),
            from_obj = [
                jobTable.
                join(assocTable, assocTable.c.job_id == jobTable.c.job_id).
                join(recoTable, assocTable.c.reconstructed_id == recoTable.c.reconstructed_id)
            ]
        )
	


class AlcaskimGetDatasetDataProvider(PagedTableDataProvider):

    def __init__(self, orderby = 0, asc = True, page = 0, pageSize = config.PAGE_SIZE):
        PagedTableDataProvider.__init__(self, orderby, asc, page, pageSize = pageSize)
        self.title = "AlcaSkim jobs"
        self.cols = Cols([
            Col("Job ID", decorator=buildAlcaSkimJobLink),
            Col("Run ID", decorator=formRunLink),
            #Col("Definition time", decorator=formatTime),  
	    Col("Definition time", decorator=formatTime),    # TODO : remove this column
            Col("Merged"),
            Col("Dataset"),
           Col("Skim"),
        ])   # TODO : complete columns in table with the ones which were in ols version

    def _buildCountQuery(self):
        sys.exit()

    def _buildMainQuery(self):
        sys.exit()
	

    def _analysis(self):
        for line in self.data:
            processedDatasetName = line[self.cols.getId("Skim")]
            processedDatasetSkimName = processedDatasetName.split('-')[1]
            line[self.cols.getId("Skim")] = processedDatasetSkimName
	     
	
################################################################################################################### STATS BY TIER

class StatsByTierDataProvider(StatsDataProvider):
	def __init__(self, inputTier=None, title = "Stats", runid = None, mergeJobs = False ):
		self.title = title
		self.qtime = 0
		self.data = []
		self.data.append([])
		self.bindParams = None
		self.inputTier = inputTier
		self.runid = runid
                if mergeJobs:
                    self.mergeSign = "="
                else:
                    self.mergeSign = "!="

	def _buildCols(self):
		self.cols = getStatsColsMergeRecoAlca(self.inputTier, self.mergeSign, self.runid)
		
	def _buildQuery(self, status):
                wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
                wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
                wmbsJobGroupTable = Tbl(TABLES.WMBS_JOBGROUP, True)
                wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
                wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
                wmbsDatasetAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
                wmbsSubscriptionTable = Tbl(TABLES.WMBS_SUBSCRIPTION, True)
                datasetTable = Tbl(TABLES.DATASET_PATH, True)
                dataTierTable = Tbl(TABLES.DATA_TIER, True)
                wmbsJobStateTable = Tbl(TABLES.WMBS_JOB_STATE, True)
		whereFragment ="WHERE"
                fromFragment = """ INNER JOIN """ + wmbsJobAssocTable + """ assoc ON (j.id = assoc.job)
                                   INNER JOIN """ + wmbsJobGroupTable + """ jg ON (jg.id = j.jobgroup ) """
		if self.inputTier != None:
			mergeAbility="Mergeable"
			fromFragment+="""  INNER JOIN """ + wmbsDatasetAssocTable  + """ a ON (a.file_id = assoc.fileid)
                                   INNER JOIN """ + datasetTable  + """ dp ON (a.dataset_path_id = dp.id) """
                        whereFragment += """  dp.data_tier = ( SELECT id FROM """ + dataTierTable + """ WHERE name='""" + self.inputTier + """' )
                                          AND """
		else: mergeAbility="ExpressMergeable"
	        whereFragment+=""" jg.subscription """ + self.mergeSign + """ ( SELECT id FROM """ + wmbsSubscriptionTable + """
                                                     WHERE fileset = ( SELECT id FROM """ + wmbsFilesetTable + """ WHERE name = '"""+ mergeAbility+ """' ) )"""
		if self.runid != None:
                        fromFragment += """ INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (assoc.fileid = m.fileid) """
                        whereFragment += """ and m.run = """ + str(self.runid)
 
                self.query = """SELECT COUNT(*)
                                       FROM (SELECT UNIQUE j.id FROM """ + wmbsJobTable + """ j """
                self.query += fromFragment
		if status == JOB_USED:
			whereFragment +=   """ AND j.state = ( SELECT id FROM """ + wmbsJobStateTable + """ WHERE name = 'created' )"""
                elif status == JOB_SUCCESS:
			whereFragment +=   """ AND j.state = ( SELECT id FROM """ + wmbsJobStateTable + """ WHERE name = 'cleanout' )
                                               AND j.outcome = 1"""
                elif status == JOB_FAILURE:
			whereFragment +=   """ AND j.state = ( SELECT id FROM """ + wmbsJobStateTable + """ WHERE name = 'cleanout' )
                                               AND j.outcome = 0"""
		else: 
			self.query = """"""
                self.query += whereFragment + """ ) """

	def load(self):
		self._buildCols()
		for i in range (JOB_USED, JOB_FAILURE + 1):
			self._buildQuery(i)
			sqlResult = executeQuery(self.query, self.bindParams)
			self.data[0].append(sqlResult.fetchone()[0])
			self.qtime += sqlResult.time
			sqlResult.close()


######################################################################################################################################### FILTERS
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################

#----------------------------------------------------------------------------------------------------------------------------------------EXPRESS


class ExpressByStatusDP(ExpressGetStreamersDataProvider):
    def __init__(self, status1,  orderby = 0, asc = True, page = 0, pageSize = config.PAGE_SIZE, status2 = None):
	ExpressGetStreamersDataProvider.__init__(self, orderby,asc,page,pageSize)
	jobTable = Tbl(TABLES.EXPRESS_JOBS)
	self.status1=status1
	if status2!=None:
	  self.status2 = status2
	  self.whereCond = or_(jobTable.c.job_status == self.status1,
	  	jobTable.c.job_status == self.status2)
	  s = JOB_STATUS_REPACKED[status1]+ ", "+ JOB_STATUS_REPACKED[status2]
	else: 
	     self.whereCond = jobTable.c.job_status == status1
	     s = JOB_STATUS_REPACKED[status1] + " "
        #self.cols["Status"].visible = False
        
        self.title = "Express " + s + " jobs"
        ExpressGetStreamersDataProvider._load(self)

class ExpressJobByStreamerIdsDP(ExpressGetStreamersDataProvider):
    def __init__(self, ids, *args, **kwds):
        ExpressGetStreamersDataProvider.__init__(self, *args, **kwds)
        assocTable = Tbl(TABLES.EXPRESS_JOB_STREAMER_ASSOC)
        jobTable = Tbl(TABLES.EXPRESS_JOBS)
        self.whereCond = jobTable.c.job_id.in_(
            select([func.distinct(assocTable.c.job_id)], assocTable.c.streamer_id.in_(ids))
        )
	self.ids = ids
	if len(ids) > 0:
          ExpressGetStreamersDataProvider._load(self)

class ExpressJobByJobIdsDP(ExpressGetStreamersDataProvider):
    def __init__(self, ids, *args, **kwds):
        ExpressGetStreamersDataProvider.__init__(self, *args, **kwds)
        jobTable = Tbl(TABLES.EXPRESS_JOBS)
        self.whereCond = jobTable.c.job_id.in_(ids)
        ExpressGetStreamersDataProvider._load(self)
	
	
class ExpressByStatusByRunDP(ExpressGetStreamersDataProvider): #same as previous one but with different table!
    def __init__(self,  status1, runid, orderby = 0, asc = True, page = 0, pageSize = config.PAGE_SIZE, status2 = None):
        ExpressGetStreamersDataProvider.__init__(self, orderby,asc,page,pageSize)
        #self.cols["Status"].visible = False
        self.cols["Run ID"].visible = False
        jobTable = Tbl(TABLES.EXPRESS_JOBS)
        streamerTable = Tbl(TABLES.STREAMER)
	self.status1=status1
	if status2!=None:
	  self.status2 = status2
	  self.whereCond = and_(or_(
            jobTable.c.job_status == status1,
	    jobTable.c.job_status == status2,),
            streamerTable.c.run_id == runid
            )
	  s = JOB_STATUS_REPACKED[status1]+ ", "+ JOB_STATUS_REPACKED[status2]
	else: 
	     self.whereCond = and_(
            jobTable.c.job_status == status1,
            streamerTable.c.run_id == runid
            )
	     s = JOB_STATUS_REPACKED[status1] + " "
        #self.cols["Status"].visible = False
        #s = JOB_STATUS_REPACKED[status]
        self.title = "Express " + s + " jobs for run " + str(runid)
        ExpressGetStreamersDataProvider._load(self)
#--------------------------------------------------------------------------------------------------------------------------------------------EXPRESS MERGE
	
class ExpressMergeByStatusDP(ExpressMergeGetFilesDataProvider):

    def __init__(self,mergeFlag, status, *args, **kwds):
        ExpressMergeGetFilesDataProvider.__init__(self, *args, **kwds)
	self.status = status
        jobTable = Tbl(TABLES.WMBS_JOB)
        #dataTierTable = Tbl(TABLES.DATA_TIER)
        subscriptionTable = Tbl(TABLES.WMBS_SUBSCRIPTION)
        jobGroupTable = Tbl(TABLES.WMBS_JOBGROUP)
        filesetTable = Tbl(TABLES.WMBS_FILESET)
        datasetPathTable = Tbl(TABLES.DATASET_PATH)
	
        if mergeFlag == "!=":
		    self.whereCond =  not_( jobGroupTable.c.subscription == \
                      select( [subscriptionTable.c.id], subscriptionTable.c.fileset == \
                              select( [filesetTable.c.id], filesetTable.c.name == 'ExpressMergeable' ) ) )
        else:
	    self.whereCond = and_(
                jobGroupTable.c.subscription == \
                    select( [subscriptionTable.c.id], subscriptionTable.c.fileset == \
                            select( [filesetTable.c.id], filesetTable.c.name == 'ExpressMergeable' ) )
                ) 		
        s = JOB_STATUS[status]
        self.title = "ExpressMerge " + " " + s + " jobs"
        ExpressMergeGetFilesDataProvider._load(self)

class ExpressMergeByStatusByRunDP(ExpressMergeGetFilesDataProvider):

    def __init__(self, mergeFlag, status, runid, *args, **kwds):
        ExpressMergeGetFilesDataProvider.__init__(self, status, *args, **kwds)
	self.status=status
        jobTable = Tbl(TABLES.WMBS_JOB)
        fileRunLumiTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP)
        #dataTierTable = Tbl(TABLES.DATA_TIER)
        subscriptionTable = Tbl(TABLES.WMBS_SUBSCRIPTION)
        jobGroupTable = Tbl(TABLES.WMBS_JOBGROUP)
        filesetTable = Tbl(TABLES.WMBS_FILESET)
        datasetPathTable = Tbl(TABLES.DATASET_PATH)
        if mergeFlag == "!=":
            self.whereCond = and_(
                fileRunLumiTable.c.run == runid,
                not_( jobGroupTable.c.subscription == \
                      select( [subscriptionTable.c.id], subscriptionTable.c.fileset == \
                               select( [filesetTable.c.id], filesetTable.c.name == 'ExpressMergeable' ) ) )
                )
        else:
            self.whereCond = and_(
                fileRunLumiTable.c.run == runid,
                jobGroupTable.c.subscription == \
                      select( [subscriptionTable.c.id], subscriptionTable.c.fileset == \
                               select( [filesetTable.c.id], filesetTable.c.name == 'ExpressMergeable' ) )
                )

        s = JOB_STATUS[status]
        self.title = "Express Merge"+ " " + s + " jobs for run " + str(runid)
        ExpressMergeGetFilesDataProvider._load(self)
	
class ExpressMergeJobByExpressIdsDP(PagedTableDataProvider):
	
    def __init__(self, ids, orderby = 0, asc = True, page = 0):
        PagedTableDataProvider.__init__(self, orderby = orderby, asc = asc, page = page)
        self.cols = Cols([
            Col("Job ID", decorator=buildExpressMergeJobLink),
            Col("Run ID", decorator=formRunLink),
            Col("Definition time", decorator=formatTime),
            Col("# of files") 
        ])
	self.title = "Express Merge jobs"
	self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
		PagedTableDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)

	self.countQuery = """ SELECT COUNT(DISTINCT j.id)
				FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                WHERE ja.fileid IN (""" + self.ids_str + """)"""

    def _buildMainQuery(self):
	wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
	wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
	wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
	datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
	primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
	wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)

	if self.asc:
                order = "ASC"
        else:
                order = "DESC"
	self.mainQuery = """ SELECT j.id, m.run, j.state_time, COUNT(DISTINCT ja.fileid)
	                     FROM """+ wmbsJobTable +""" j 
			     INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job) 
			     INNER JOIN """ + wmbsFileDetailsTable + """ f ON (f.id = ja.fileid)
			     INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
			     WHERE ja.fileid IN (""" + self.ids_str + """)
			     GROUP BY j.id, m.run,j.state_time	
			     ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order
      


class ExpressMergeJobByIdsDP(PagedTableDataProvider):
    def __init__(self, ids, *args, **kwds):
        PagedTableDataProvider.__init__(self, *args, **kwds)
        self.cols = Cols([
            Col("Job ID", decorator=buildExpressMergeJobLink),
            Col("Run ID", decorator=formRunLink),
            Col("Definition time", decorator=formatTime),
            Col("# of files") 
        ])
        self.title = "Express Merge jobs"
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
                PagedTableDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)

        self.countQuery = """ SELECT COUNT(DISTINCT id)
                                FROM """ + wmbsJobTable + """ 
                                WHERE id IN (""" + self.ids_str + """)"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)

        if self.asc:
                order = "ASC"
        else:
                order = "DESC"

        self.mainQuery = """ SELECT j.id, m.run, j.state_time, COUNT(DISTINCT ja.fileid)
	                     FROM """+ wmbsJobTable +""" j 
			     INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job) 
			     INNER JOIN """ + wmbsFileDetailsTable + """ f ON (f.id = ja.fileid)
			     INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
			     WHERE j.id IN (""" + self.ids_str + """)
			     GROUP BY j.id, m.run,j.state_time	
			     ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order
				
class ExpressMergeJobByExpressMergeIdsDP(PagedTableDataProvider):
    def __init__(self, ids, *args, **kwds):
        PagedTableDataProvider.__init__(self, *args, **kwds)
        self.cols = Cols([
            Col("Job ID", decorator=buildExpressMergeJobLink),
            Col("Run ID", decorator=formRunLink),
            Col("Definition time", decorator=formatTime),
            Col("# of files") 
        ])
        self.title = "Express Merge jobs"
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
                PagedTableDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        self.countQuery = """ SELECT COUNT(DISTINCT j.id)
                                FROM """ + wmbsJobTable + """ j 
                                WHERE j.id IN (SELECT job FROM """ + wmbsJobAssocTable + """ INNER JOIN """ + wmbsFileParentTable + """ ON (parent = fileid)
 WHERE child IN (""" + self.ids_str + """))"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
	wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)

        if self.asc:
                order = "ASC"
        else:
                order = "DESC"

        self.mainQuery = """ SELECT j.id, m.run, j.state_time, COUNT(DISTINCT ja.fileid)
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                                WHERE ja.job IN (SELECT job FROM """ + wmbsJobAssocTable + """ INNER JOIN """ + wmbsFileParentTable + """ ON (parent = fileid) WHERE child IN (""" + self.ids_str + """))
                                GROUP BY j.id, m.run, j.state_time
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order

#-------------------------------------------------------------------------------------------------------------------------------------------REPACK 
class RepackJobByStreamerIdsDP(BaseRepackJobDP):
    def __init__(self, ids, *args, **kwds):
        BaseRepackJobDP.__init__(self, *args, **kwds)
        assocTable = Tbl(TABLES.JOB_DATASET_STREAMER_ASSOC)
        jobTable = Tbl(TABLES.REPACK_JOBS)
        self.whereCond = jobTable.c.job_id.in_(
            select([func.distinct(assocTable.c.job_id)], assocTable.c.streamer_id.in_(ids))
        )
        BaseRepackJobDP._load(self)

class RepackJobByJobIdsDP(BaseRepackJobDP):
    def __init__(self, ids, *args, **kwds):
        BaseRepackJobDP.__init__(self, *args, **kwds)
        jobTable = Tbl(TABLES.REPACK_JOBS)
        self.whereCond = jobTable.c.job_id.in_(ids)
        BaseRepackJobDP._load(self)

class RepackJobByRepackIdsDP(BaseRepackJobDP): # used????
    def __init__(self, ids, *args, **kwds):
        BaseRepackJobDP.__init__(self, *args, **kwds)
        assocTable1 = Tbl(TABLES.JOB_DATASET_STREAMER_ASSOC)
        assocTable2 = Tbl(TABLES.REPACK_STREAMER_ASSOC)
        jobTable = Tbl(TABLES.REPACK_JOBS)
        self.whereCond = jobTable.c.job_id.in_(
            select([func.distinct(assocTable1.c.job_id)], 
			assocTable1.c.streamer_id.in_(select([assocTable2.c.streamer_id], assocTable2.c.repacked_id.in_(ids)))
            )
        )
        BaseRepackJobDP._load(self)
	
class RepackRunningJobDP(BaseRepackJobDP):
    def __init__(self, *args, **kwds):
        #kwds['pageSize'] = 25
        BaseRepackJobDP.__init__(self, *args, **kwds)
        self.cols[2] = Col("Running time", decorator=deltaTime)
        self.cols["Status"].visible = False
        jobTable = Tbl(TABLES.REPACK_JOBS)
        self.whereCond = or_(
            jobTable.c.job_status == JOB_USED,
            jobTable.c.job_status == JOB_NEW,
        )
        self.title = "Repack running jobs"
        BaseRepackJobDP._load(self)
	

class RepackJobByStatusDP(BaseRepackJobDP):

    def __init__(self, status, *args, **kwds):
        BaseRepackJobDP.__init__(self, *args, **kwds)
        self.cols["Status"].visible = False
        jobTable = Tbl(TABLES.REPACK_JOBS)
        self.whereCond = jobTable.c.job_status == status
        s = JOB_STATUS_REPACKED[status]
        self.title = "Repacker " + s + " jobs"
        BaseRepackJobDP._load(self)
	


class RepackJobByStatusByRunDP(BaseRepackJobDP):
    def __init__(self, status, runid, *args, **kwds):
        BaseRepackJobDP.__init__(self, *args, **kwds)
        self.cols["Status"].visible = False
        self.cols["Run ID"].visible = False
        jobTable = Tbl(TABLES.REPACK_JOBS)
        streamerTable = Tbl(TABLES.STREAMER)
        self.whereCond = and_(
            jobTable.c.job_status == status,
            streamerTable.c.run_id == runid
            )

        s = JOB_STATUS_REPACKED[status]
        self.title = "Repacker " + s + " jobs for run " + str(runid)
        BaseRepackJobDP._load(self)

#------------------------------------------------------------------------------------------------------------------------------------REPACK MERGE 
class RepackMergeJobByRepackIdsDP(RepackMergeGetDatasetDataProvider):
	
    def __init__(self, ids, *args, **kwds):
        RepackMergeGetDatasetDataProvider.__init__(self, *args, **kwds)
        self.cols = Cols([
            Col("Job ID", decorator=buildRepackMergeJobLink),
            Col("Run ID", decorator=formRunLink),
            #Col("Definition time", decorator=formatTime),
            Col("Repacked"),
            Col("Dataset")
#            Col("Status")   ## How to get the status of the job?
        ])
	self.title = "Repack Merge jobs"
	self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
		RepackMergeGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)

	self.countQuery = """ SELECT COUNT(DISTINCT j.id)
				FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                WHERE ja.fileid IN (""" + self.ids_str + """)"""

    def _buildMainQuery(self):
	wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
	wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
	wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
	datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
	primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
	wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)

	if self.asc:
                order = "ASC"
        else:
                order = "DESC"

        self.mainQuery = """ SELECT j.id, m.run, COUNT(DISTINCT ja.fileid), pd.name
				FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
				 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
				 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
				 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
				 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
				WHERE ja.job IN (SELECT job FROM """ + wmbsJobAssocTable + """ WHERE fileid IN (""" + self.ids_str + """))
				GROUP BY j.id, m.run, pd.name
				ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order
				

	




class RepackMergeJobByRepackMergeIdsDP(RepackMergeGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        RepackMergeGetDatasetDataProvider.__init__(self, *args, **kwds)
        self.cols = Cols([
            Col("Job ID", decorator=buildRepackMergeJobLink),
            Col("Run ID", decorator=formRunLink),
            Col("Definition time", decorator=formatTime),
            Col("Repacked"),
            Col("Dataset")
#            Col("Status")   ## How to get the status of the job?
        ])
        self.title = "Repack Merge jobs"
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
                RepackMergeGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        self.countQuery = """ SELECT COUNT(DISTINCT j.id)
                                FROM """ + wmbsJobTable + """ j 
                                WHERE j.id IN (SELECT job FROM """ + wmbsJobAssocTable + """ INNER JOIN """ + wmbsFileParentTable + """ ON (parent = fileid)
 WHERE child IN (""" + self.ids_str + """))"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
	wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)

        if self.asc:
                order = "ASC"
        else:
                order = "DESC"

        self.mainQuery = """ SELECT j.id, m.run, j.state_time, COUNT(DISTINCT ja.fileid), pd.name
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                                WHERE ja.job IN (SELECT job FROM """ + wmbsJobAssocTable + """ INNER JOIN """ + wmbsFileParentTable + """ ON (parent = fileid) WHERE child IN (""" + self.ids_str + """))
                                GROUP BY j.id, m.run, j.state_time, pd.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order



class RepackMergeJobByJobIdsDP(RepackMergeGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        RepackMergeGetDatasetDataProvider.__init__(self, *args, **kwds)
        self.cols = Cols([
            Col("Job ID", decorator=buildRepackMergeJobLink),
            Col("Run ID", decorator=formRunLink),
            Col("Definition time", decorator=formatTime),
            Col("Repacked"),
            Col("Dataset")
#            Col("Status")   ## How to get the status of the job?
        ])
        self.title = "Repack Merge jobs"
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
                RepackMergeGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)

        self.countQuery = """ SELECT COUNT(DISTINCT id)
                                FROM """ + wmbsJobTable + """ 
                                WHERE id IN (""" + self.ids_str + """)"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)

        if self.asc:
                order = "ASC"
        else:
                order = "DESC"

        self.mainQuery = """ SELECT j.id, m.run, j.state_time, COUNT(DISTINCT ja.fileid), pd.name
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                                WHERE j.id IN (""" + self.ids_str + """)
                                GROUP BY j.id, m.run, j.state_time, pd.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order



class RepackMergeJobByStatusDP(RepackMergeGetDatasetDataProvider):

    def __init__(self, status, *args, **kwds):
        RepackMergeGetDatasetDataProvider.__init__(self, *args, **kwds)
        self.cols["Status"].visible = False
        jobTable = Tbl(TABLES.MERGE_JOBS)
        self.whereCond = jobTable.c.job_status == status
        s = JOB_STATUS[status]
        self.title = "Merge " + s + " jobs"
        RepackMergeGetDatasetDataProvider._load(self)

#-----------------------------------------------------------------------------------------------------------------------------------------------------RECO 
class RecoJobByMergeIdsDP(RecoGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        RecoGetDatasetDataProvider.__init__(self, *args, **kwds)
	self.cols[3] = Col("Files")
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
		RecoGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)

        self.countQuery = """ SELECT COUNT(DISTINCT j.id)
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                WHERE ja.fileid IN (""" + self.ids_str + """)"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)

        if self.asc:
                order = "ASC"
        else:
                order = "DESC"
        # orig version has a  "j.last_update," I changed it to j.state_time
        self.mainQuery = """ SELECT j.id, m.run,  j.state_time,COUNT(DISTINCT ja.fileid), pd.name
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                                WHERE ja.job IN (SELECT job FROM """ + wmbsJobAssocTable + """ WHERE fileid IN (""" + self.ids_str + """))
                                GROUP BY j.id, m.run,j.state_time, pd.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order



class RecoJobByRecoIdsDP(RecoGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        RecoGetDatasetDataProvider.__init__(self, *args, **kwds)
        self.cols[3] = Col("Files")
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
                RecoGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        self.countQuery = """ SELECT COUNT(DISTINCT j.id)
                                FROM """ + wmbsJobTable + """ j
                                WHERE j.id IN (SELECT job FROM """ + wmbsJobAssocTable + """ INNER JOIN """ + wmbsFileParentTable + """ ON (parent = fileid)
 WHERE child IN (""" + self.ids_str + """))"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)

        if self.asc:
                order = "ASC"
        else:
                order = "DESC"

        self.mainQuery = """ SELECT j.id, m.run, j.state_time,COUNT(DISTINCT ja.fileid), pd.name
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                                WHERE ja.job IN (SELECT job FROM """ + wmbsJobAssocTable + """ INNER JOIN """ + wmbsFileParentTable + """ ON (parent = fileid) WHERE child IN (""" + self.ids_str + """))
                                GROUP BY j.id, m.run, j.state_time, pd.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order

	

class RecoJobByJobIdsDP(RecoGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        RecoGetDatasetDataProvider.__init__(self, *args, **kwds)
        self.cols[3] = Col("Files")
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
                RecoGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)

        self.countQuery = """ SELECT COUNT(DISTINCT id)
                                FROM """ + wmbsJobTable + """ 
                                WHERE id IN (""" + self.ids_str + """)"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)

        if self.asc:
                order = "ASC"
        else:
                order = "DESC"
   	# changed start -> state
        self.mainQuery = """ SELECT j.id, m.run, j.state_time, COUNT(DISTINCT ja.fileid), pd.name
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                                WHERE j.id IN (""" + self.ids_str + """)
                                GROUP BY j.id, m.run, j.state_time, pd.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order



#-----------------------------------------------------------------------------------------------------------------------------------------RECO MERGE
class RecoMergeJobByRecoIdsDP(RecoGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        RecoGetDatasetDataProvider.__init__(self, *args, **kwds)
	self.title = "Reco Merge jobs"
	self.cols["Job ID"].decorator = buildRecoMergeJobLink
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
        	RecoGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)

        self.countQuery = """ SELECT COUNT(DISTINCT j.id)
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                WHERE ja.fileid IN (""" + self.ids_str + """)"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)

        if self.asc:
                order = "ASC"
        else:
                order = "DESC"
	# changed j.last_update
        self.mainQuery = """ SELECT j.id, m.run,j.state_time,  COUNT(DISTINCT ja.fileid), pd.name
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                                WHERE ja.job IN (SELECT job FROM """ + wmbsJobAssocTable + """ WHERE fileid IN (""" + self.ids_str + """))
                                GROUP BY j.id, m.run,state_time, pd.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order


class RecoMergeJobByJobIdsDP(RecoGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        RecoGetDatasetDataProvider.__init__(self, *args, **kwds)
        self.title = "Reco Merge jobs"
        self.cols["Job ID"].decorator = buildRecoMergeJobLink
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
                RecoGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)

        self.countQuery = """ SELECT COUNT(DISTINCT id)
                                FROM """ + wmbsJobTable + """ 
                                WHERE id IN (""" + self.ids_str + """)"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)

        if self.asc:
                order = "ASC"
        else:
                order = "DESC"
	# changed j.last_update
        self.mainQuery = """ SELECT j.id, m.run, j.state_time, COUNT(DISTINCT ja.fileid), pd.name
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                                WHERE j.id IN (""" + self.ids_str + """)
                                GROUP BY j.id, m.run,j.state_time, pd.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order


class RecoMergeJobByRecoMergeIdsDP(RecoGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        RecoGetDatasetDataProvider.__init__(self, *args, **kwds)
        self.title = "Reco Merge jobs"
        self.cols["Job ID"].decorator = buildRecoMergeJobLink
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
                RecoGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)

        self.countQuery = """ SELECT COUNT(DISTINCT j.id)
                                FROM """ + wmbsJobTable + """ j 
                                WHERE j.id IN (SELECT job FROM """ + wmbsJobAssocTable + """ INNER JOIN """ + wmbsFileParentTable + """ ON (parent = fileid) WHERE child IN (""" + self.ids_str + """))"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
	wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)

        if self.asc:
                order = "ASC"
        else:
                order = "DESC"
	# changed j.last_update
        self.mainQuery = """ SELECT j.id, m.run,j.state_time,  COUNT(DISTINCT ja.fileid), pd.name
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                                WHERE ja.job IN (SELECT job FROM """ + wmbsJobAssocTable + """ INNER JOIN """ + wmbsFileParentTable + """ ON (parent = fileid) WHERE child IN (""" + self.ids_str + """))
                                GROUP BY j.id, m.run, j.state_time, pd.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order

#-------------------------------------------------------------------------------------------------------------------------------------ALCA

class AlcaSkimJobByRecoMergeIdsDP(AlcaskimGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        AlcaskimGetDatasetDataProvider.__init__(self, *args, **kwds)
	
	self.cols[3] = Col("Files")
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
	        AlcaskimGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)

        self.countQuery = """ SELECT COUNT(DISTINCT j.id)
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                WHERE ja.fileid IN (""" + self.ids_str + """)"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
	processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)
        if self.asc:
                order = "ASC"
        else:
                order = "DESC"
	# changed j.last_update
        self.mainQuery = """ SELECT j.id, m.run, j.state_time, COUNT(DISTINCT ja.fileid), pd.name, proc.name as skim
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
				  INNER JOIN """ + processedDatasetTable + """ proc ON (dp.processed_dataset = proc.id)
                                WHERE ja.job IN (SELECT job FROM """ + wmbsJobAssocTable + """ WHERE fileid IN (""" + self.ids_str + """))
                                GROUP BY j.id, m.run, j.state_time, pd.name,proc.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order


class AlcaSkimJobByRecoIdsDP(AlcaskimGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        AlcaskimGetDatasetDataProvider.__init__(self, *args, **kwds)
	self.cols[3] = Col("Files")
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
	        AlcaskimGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)

        self.countQuery = """ SELECT COUNT(DISTINCT j.id)
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                WHERE ja.fileid IN (""" + self.ids_str + """)"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
	dataTierTable = Tbl(TABLES.DATA_TIER, True)
	wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
        wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
	processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)
        if self.asc:
                order = "ASC"
        else:
                order = "DESC"
	# changed j.last_update
        self.mainQuery = """ SELECT j.id, m.run, j.state_time, COUNT(DISTINCT ja.fileid), pd.name, proc.name as skim
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
				 INNER JOIN """ + dataTierTable + """ dt ON (dp.data_tier = dt.id)
                           	 INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                            	INNER JOIN """ + wmbsFilesetTable + """ fs ON (fs.id = fsf.fileset)
				INNER JOIN """ + processedDatasetTable + """ proc ON (dp.processed_dataset = proc.id)
                                WHERE ja.job IN (
				         SELECT job FROM """ + wmbsJobAssocTable + """ 
				         WHERE fileid IN (""" + self.ids_str + """))
				     AND dt.name='ALCARECO' and fs.name = 'AlcaSkimmable'
                                GROUP BY j.id, m.run, j.state_time, pd.name,proc.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order

class AlcaSkimJobByAlcaSkimIdsDP(AlcaskimGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        AlcaskimGetDatasetDataProvider.__init__(self, *args, **kwds)
        self.cols[3] = Col("Files")
	
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
                AlcaskimGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        self.countQuery = """ SELECT COUNT(DISTINCT j.id)
                                FROM """ + wmbsJobTable + """ j
                                WHERE j.id IN (SELECT job FROM """ + wmbsJobAssocTable + """ INNER JOIN """ + wmbsFileParentTable + """ ON (parent = fileid)
 WHERE child IN (""" + self.ids_str + """))"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
	processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)
        if self.asc:
                order = "ASC"
        else:
                order = "DESC"
	# changed j.last_update
        self.mainQuery = """ SELECT j.id, m.run,j.state_time,  COUNT(DISTINCT ja.fileid), pd.name, proc.name as skim
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
				 INNER JOIN """ + processedDatasetTable + """ proc ON (dp.processed_dataset = proc.id)
                                WHERE ja.job IN (SELECT job FROM """ + wmbsJobAssocTable + """ INNER JOIN """ + wmbsFileParentTable + """ ON (parent = fileid) WHERE child IN (""" + self.ids_str + """))
                                GROUP BY j.id, m.run,j.state_time,  pd.name,proc.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order

class AlcaSkimJobByJobIdsDP(AlcaskimGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        AlcaskimGetDatasetDataProvider.__init__(self, *args, **kwds)
        self.cols[3] = Col("Files")
	
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
                AlcaskimGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)

        self.countQuery = """ SELECT COUNT(DISTINCT id)
                                FROM """ + wmbsJobTable + """
                                WHERE id IN (""" + self.ids_str + """)"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
	processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)
        if self.asc:
                order = "ASC"
        else:
                order = "DESC"
	# changed j.last_update
        self.mainQuery = """ SELECT j.id, m.run,j.state_time, COUNT(DISTINCT ja.fileid), pd.name, proc.name as skim
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
				 INNER JOIN """ + processedDatasetTable + """ proc ON (dp.processed_dataset = proc.id)
                                WHERE j.id IN (""" + self.ids_str + """)
                                GROUP BY j.id, m.run,j.state_time, pd.name,proc.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order
	#print self.mainQuery


#-----------------------------------------------------------------------------------------------------------------------------------------------------ALCASKIM MERGE

class AlcaSkimMergeJobByJobIdsDP(AlcaskimGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        AlcaskimGetDatasetDataProvider.__init__(self, *args, **kwds)
        self.title = "AlcaSkim Merge jobs"
        self.cols["Job ID"].decorator = buildAlcaSkimMergeJobLink
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
                AlcaskimGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)

        self.countQuery = """ SELECT COUNT(DISTINCT id)
                                FROM """ + wmbsJobTable + """
                                WHERE id IN (""" + self.ids_str + """)"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
	processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)
        if self.asc:
                order = "ASC"
        else:
                order = "DESC"
	# changed j.last_update
        self.mainQuery = """ SELECT j.id, m.run,j.state_time, COUNT(DISTINCT ja.fileid), pd.name,pds.name as skim
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
				 INNER JOIN """ + processedDatasetTable + """ pds ON (dp.processed_dataset = pds.id)
                                WHERE j.id IN (""" + self.ids_str + """)
                                GROUP BY j.id, m.run,j.state_time, pd.name,pds.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order


class AlcaSkimMergeJobByAlcaSkimIdsDP(AlcaskimGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        AlcaskimGetDatasetDataProvider.__init__(self, *args, **kwds)
	self.title = "AlcaSkim Merge jobs"
	self.cols["Job ID"].decorator = buildAlcaSkimMergeJobLink
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
                AlcaskimGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)

        self.countQuery = """ SELECT COUNT(DISTINCT j.id)
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                WHERE ja.fileid IN (""" + self.ids_str + """)"""

    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
	processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)
        if self.asc:
                order = "ASC"
        else:
                order = "DESC"

        self.mainQuery = """ SELECT j.id, m.run,j.state_time, COUNT(DISTINCT ja.fileid), pd.name,pds.name as skim
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
				 INNER JOIN """ + processedDatasetTable + """ pds ON (dp.processed_dataset = pds.id)
                                WHERE ja.job IN (SELECT job FROM """ + wmbsJobAssocTable + """ WHERE fileid IN (""" + self.ids_str + """))
                                GROUP BY j.id, m.run,j.state_time, pd.name,pds.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order



class AlcaSkimMergeJobByAlcaSkimMergeIdsDP(AlcaskimGetDatasetDataProvider):
    def __init__(self, ids, *args, **kwds):
        AlcaskimGetDatasetDataProvider.__init__(self, *args, **kwds)
        self.title = "AlcaSkim Merge jobs"
        self.cols["Job ID"].decorator = buildAlcaSkimMergeJobLink
        self.ids = ids
        self.ids_str = ""
        numIds = len(self.ids)
        if numIds != 0:
                if numIds > 1:
                        for i in range(numIds-1):
                                self.ids_str += str(self.ids[i]) + ", "
                self.ids_str += str(self.ids[-1])
                AlcaskimGetDatasetDataProvider._load(self)

    def _buildCountQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
        wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)

        self.countQuery = """ SELECT COUNT(DISTINCT j.id)
                                FROM """ + wmbsJobTable + """ j 
                                WHERE j.id IN (SELECT job FROM """ + wmbsJobAssocTable + """ INNER JOIN """ + wmbsFileParentTable + """ ON (parent = fileid) WHERE child IN (""" + self.ids_str + """))"""


    def _buildMainQuery(self):
        wmbsJobTable = Tbl(TABLES.WMBS_JOB, True)
        wmbsJobAssocTable = Tbl(TABLES.WMBS_JOB_ASSOC, True)
	wmbsFileParentTable = Tbl(TABLES.WMBS_FILE_PARENT, True)
        wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
        wmbsFileDatasetPathAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
        datasetPathTable = Tbl(TABLES.DATASET_PATH, True)
        primaryDatasetTable = Tbl(TABLES.PRIMARY_DATASET, True)
        wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
	processedDatasetTable = Tbl(TABLES.PROCESSED_DATASET, True)
        if self.asc:
                order = "ASC"
        else:
                order = "DESC"
	# changed j.last_update
        self.mainQuery = """ SELECT j.id, m.run,j.state_time, COUNT(DISTINCT ja.fileid), pd.name,pds.name as skim
                                FROM """ + wmbsJobTable + """ j INNER JOIN """ + wmbsJobAssocTable + """ ja ON (j.id = ja.job)
                                 INNER JOIN """ + wmbsFileDetailsTable + """ f ON (ja.fileid = f.id)
                                 INNER JOIN """ + wmbsFileDatasetPathAssocTable + """ a ON (a.file_id = f.id)
                                 INNER JOIN """ + datasetPathTable + """ dp ON (dp.id = a.dataset_path_id)
                                 INNER JOIN """ + primaryDatasetTable + """ pd ON (pd.id = dp.primary_dataset)
                                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
				  INNER JOIN """ + processedDatasetTable + """ pds ON (dp.processed_dataset = pds.id)
                                WHERE ja.job IN (SELECT job FROM """ + wmbsJobAssocTable + """ INNER JOIN """ + wmbsFileParentTable + """ ON (parent = fileid) WHERE child IN (""" + self.ids_str + """))
                                GROUP BY j.id, m.run,j.state_time,  pd.name,pds.name
                                ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order

#--------------------------------------------------------------------------------------------------------------------------------------------- WMBS
#-------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------


class BaseWMBSJobDP(PagedTableDataProvider):
    def __init__(self, status, orderby = 0, asc = True, page = 0, pageSize = config.PAGE_SIZE):
        PagedTableDataProvider.__init__(self, orderby, asc, page, pageSize = pageSize)
        self.title = "WMBS jobs"
        self.status = status
        self.cols = Cols([
            Col("Job ID", decorator=buildRepackJobLink),
            Col("Run ID", decorator=formRunLink),
            Col("Definition time", decorator=formatTime),
            Col("# of files"), 
            Col("Dataset"),
            Col("Status")
        ])

    def _buildCountQuery(self):
        jobTable = Tbl(TABLES.WMBS_JOB)
        jobTableState = Tbl(TABLES.WMBS_JOB_STATE)
        jobGroupTable = Tbl(TABLES.WMBS_JOBGROUP)
        assocTable = Tbl(TABLES.WMBS_JOB_ASSOC)
        fileTable = Tbl(TABLES.WMBS_FILE_DETAILS)
        fileRunLumiTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP)
        fileDatasetPathTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC)
        datasetPathTable = Tbl(TABLES.DATASET_PATH)
        datasetTable = Tbl(TABLES.PRIMARY_DATASET)
        if self.status == "ACQUIRED":
            jobSelection = and_( jobTable.c.state == select( [jobTableState.c.id], jobTableState.c.name == 'created' ) )
        elif self.status == "COMPLETE":
            jobSelection = and_( jobTable.c.state == select( [jobTableState.c.id], jobTableState.c.name == 'cleanout' ),
                                 jobTable.c.outcome == 1 )
            
        elif self.status == "FAILED":
            jobSelection = and_( jobTable.c.state == select( [jobTableState.c.id], jobTableState.c.name == 'cleanout' ),
                                 jobTable.c.outcome == 0 )
        else:
            print "Unknown state request: %s" % self.status
            
      
        self.countQuery = select(
            [func.count(func.distinct(jobTable.c.id))],
            and_( self.whereCond, jobSelection ),
            from_obj = [
                jobTable.
                join(jobGroupTable, jobTable.c.jobgroup == jobGroupTable.c.id).
                join(assocTable, jobTable.c.id == assocTable.c.job).
                join(fileTable, fileTable.c.id == assocTable.c.fileid).
                join(fileRunLumiTable, fileTable.c.id == fileRunLumiTable.c.fileid).
                join(fileDatasetPathTable, fileTable.c.id == fileDatasetPathTable.c.file_id).
                join(datasetPathTable, fileDatasetPathTable.c.dataset_path_id == datasetPathTable.c.id).
                join(datasetTable, datasetTable.c.id == datasetPathTable.c.primary_dataset)
            ]
        )

    def _buildMainQuery(self):
        jobTable = Tbl(TABLES.WMBS_JOB)
        jobTableState = Tbl(TABLES.WMBS_JOB_STATE)
        jobGroupTable = Tbl(TABLES.WMBS_JOBGROUP)
        assocTable = Tbl(TABLES.WMBS_JOB_ASSOC)
        fileTable = Tbl(TABLES.WMBS_FILE_DETAILS)
        fileRunLumiTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP)
        fileDatasetPathTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC)
        datasetPathTable = Tbl(TABLES.DATASET_PATH)
        datasetTable = Tbl(TABLES.PRIMARY_DATASET)
        if self.status == "ACQUIRED":
            jobSelection = and_( jobTable.c.state == select( [jobTableState.c.id], jobTableState.c.name == 'created' ) )
        elif self.status == "COMPLETE":
            jobSelection = and_( jobTable.c.state == select( [jobTableState.c.id], jobTableState.c.name == 'cleanout' ),
                                 jobTable.c.outcome == 1 )
            
        elif self.status == "FAILED":
            jobSelection = and_( jobTable.c.state == select( [jobTableState.c.id], jobTableState.c.name == 'cleanout' ),
                                 jobTable.c.outcome == 0 )
        else:
            print "Unknown state request: %s" % self.status
	c = (
             jobTable.c.id,
             fileRunLumiTable.c.run,
             jobTable.c.state_time,
             func.count(func.distinct(assocTable.c.fileid)).label("Input Files"),
             datasetTable.c.name
         )
        if self.asc: o = c[self.orderby].asc()
        else: o = c[self.orderby].desc()
        self.mainQuery = select(
            c,
            and_(self.whereCond, jobSelection ),
            from_obj = [
                jobTable.
                join(jobGroupTable, jobTable.c.jobgroup == jobGroupTable.c.id).
                join(assocTable, jobTable.c.id == assocTable.c.job).
                join(fileTable, fileTable.c.id == assocTable.c.fileid).
                join(fileRunLumiTable, fileTable.c.id == fileRunLumiTable.c.fileid).
                join(fileDatasetPathTable, fileTable.c.id == fileDatasetPathTable.c.file_id).
                join(datasetPathTable, fileDatasetPathTable.c.dataset_path_id == datasetPathTable.c.id).
                join(datasetTable, datasetTable.c.id == datasetPathTable.c.primary_dataset)
            ]
            ).group_by(
                jobTable.c.id,
                jobTable.c.state_time,
                fileRunLumiTable.c.run,
                datasetTable.c.name
            ).order_by(o)



############################################################################### next 2 classes may be merged togheter
class WMBSByTierByStatusDP(BaseWMBSJobDP):	
    def __init__(self, inputTier, mergeFlag, status, *args, **kwds):
        BaseWMBSJobDP.__init__(self, status, *args, **kwds)
        self.cols["Status"].visible = False
	if inputTier == "RAW":
		if mergeFlag == "!=":
			self.cols["Job ID"].decorator = buildRecoJobLink
		else:
                        self.cols["Job ID"].decorator = buildRepackMergeJobLink
	elif inputTier == "RECO":
                if mergeFlag == "!=":
                        self.cols["Job ID"].decorator = buildAlcaSkimJobLink
                else:
                        self.cols["Job ID"].decorator = buildRecoMergeJobLink
	elif inputTier == "ALCARECO":
                if mergeFlag == "!=":
                        self.cols["Job ID"].decorator = buildAlcaSkimJobLink
                else:
                        self.cols["Job ID"].decorator = buildAlcaSkimMergeJobLink
        jobTable = Tbl(TABLES.WMBS_JOB)
        dataTierTable = Tbl(TABLES.DATA_TIER)
        subscriptionTable = Tbl(TABLES.WMBS_SUBSCRIPTION)
        jobGroupTable = Tbl(TABLES.WMBS_JOBGROUP)
        filesetTable = Tbl(TABLES.WMBS_FILESET)
        datasetPathTable = Tbl(TABLES.DATASET_PATH)
	if inputTier ==None:
		self.fileset = 'ExpressMergeable'
		if mergeFlag == "!=":
		    	self.whereCond =  not_( jobGroupTable.c.subscription == \
                      		select( [subscriptionTable.c.id], subscriptionTable.c.fileset == \
                              	select( [filesetTable.c.id], filesetTable.c.name == self.fileset ) ) )
                else:
	    		self.whereCond = and_(
                		jobGroupTable.c.subscription == \
                    		select( [subscriptionTable.c.id], subscriptionTable.c.fileset == \
                            	select( [filesetTable.c.id], filesetTable.c.name == self.fileset ) )
                		) 	
	else: 
		self.fileset = 'Mergeable'
        	if mergeFlag == "!=":
		    	self.whereCond =  and_( datasetPathTable.c.data_tier == select( [dataTierTable.c.id], dataTierTable.c.name == inputTier), \
			        not_( jobGroupTable.c.subscription == \
                      		select( [subscriptionTable.c.id], subscriptionTable.c.fileset == \
                              	select( [filesetTable.c.id], filesetTable.c.name == self.fileset ) ) ))
                else:
	    		self.whereCond = and_(  datasetPathTable.c.data_tier == select( [dataTierTable.c.id], dataTierTable.c.name == inputTier ), \
                		jobGroupTable.c.subscription == \
                    		select( [subscriptionTable.c.id], subscriptionTable.c.fileset == \
                            	select( [filesetTable.c.id], filesetTable.c.name == self.fileset ) )
                		) 	
        s = JOB_STATUS[status]
        t = JOB_TYPE[inputTier][mergeFlag]
        self.title = t + " " + s + " jobs"
        BaseWMBSJobDP._load(self)

class WMBSByTierByStatusByRunDP(BaseWMBSJobDP):
    def __init__(self, inputTier, mergeFlag, status, runid, *args, **kwds):
        BaseWMBSJobDP.__init__(self, status, *args, **kwds)
        self.cols["Run ID"].visible = False
        self.cols["Status"].visible = False
        if inputTier == "RAW":
            if mergeFlag == "!=":
                self.cols["Job ID"].decorator = buildRecoJobLink
            else:
                self.cols["Job ID"].decorator = buildRepackMergeJobLink
        elif inputTier == "RECO":
            if mergeFlag == "!=":
                self.cols["Job ID"].decorator = buildAlcaSkimJobLink
            else:
                self.cols["Job ID"].decorator = buildRecoMergeJobLink
        elif inputTier == "ALCARECO":
            if mergeFlag == "!=":
                self.cols["Job ID"].decorator = buildAlcaSkimJobLink
            else:
                self.cols["Job ID"].decorator = buildAlcaSkimMergeJobLink
      
        jobTable = Tbl(TABLES.WMBS_JOB)
        fileRunLumiTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP)
        dataTierTable = Tbl(TABLES.DATA_TIER)
        subscriptionTable = Tbl(TABLES.WMBS_SUBSCRIPTION)
        jobGroupTable = Tbl(TABLES.WMBS_JOBGROUP)
        filesetTable = Tbl(TABLES.WMBS_FILESET)
        datasetPathTable = Tbl(TABLES.DATASET_PATH)
        if mergeFlag == "!=":
            self.whereCond = and_(
                datasetPathTable.c.data_tier == select( [dataTierTable.c.id], dataTierTable.c.name == inputTier ),
                fileRunLumiTable.c.run == runid,
                not_( jobGroupTable.c.subscription == \
                      select( [subscriptionTable.c.id], subscriptionTable.c.fileset == \
                               select( [filesetTable.c.id], filesetTable.c.name == 'Mergeable' ) ) )
                )
        else:
            self.whereCond = and_(
                datasetPathTable.c.data_tier == select( [dataTierTable.c.id], dataTierTable.c.name == inputTier ),
                fileRunLumiTable.c.run == runid,
                jobGroupTable.c.subscription == \
                      select( [subscriptionTable.c.id], subscriptionTable.c.fileset == \
                               select( [filesetTable.c.id], filesetTable.c.name == 'Mergeable' ) )
                )
	
        t = JOB_TYPE[inputTier][mergeFlag]
        s = JOB_STATUS[status]
        self.title = t+ " " + s + " jobs for run " + str(runid)
        BaseWMBSJobDP._load(self)
	
	
	
