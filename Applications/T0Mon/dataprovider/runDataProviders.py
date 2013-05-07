from sqlalchemy import *

from dataProviderBase import *
from T0Mon.utils import *
from T0Mon.analysis import *
from T0Mon.consts import *
from T0Mon.sqlManager import *

from T0Mon.globals import logger
import T0Mon.config

### Module for classes providing data about T0 runs ###

class RunConfigKeyProvider(TableDataProvider):
    col1 = [Col("Dataset"), Cols([])]
    col2 = [Col("Repack"), Cols([Col("Proc Version")])]
    col3 = [Col("Reco"), Cols([Col("Reco"), Col("CMSsw Version"), Col("Global tag"), Col("Config URL", decorator=buildWebLink), Col("Proc Version")])]
    col4 = [Col("AlcaSkim"), Cols([Col("AlcaSkim"), Col("CMSsw Version"), Col("Config URL", decorator=buildWebLink), Col("Proc Version")])]
    columns = []
    columns.append(col1)
    columns.append(col2)
    columns.append(col3)
    columns.append(col4)

    cols = DoubleCols(columns)

    def __init__(self, runid):
        self.runid = runid
        self.title = "Run " + str(self.runid)
        TableDataProvider.__init__(self)
        TableDataProvider._load(self)

    def _buildQuery(self):
        repackConfig = Tbl(TABLES.REPACK_CONFIG, True)
        recoConfig = Tbl(TABLES.RECO_CONFIG, True)
	alcaConfig = Tbl(TABLES.ALCA_CONFIG, True)
        primaryDataset = Tbl(TABLES.PRIMARY_DATASET, True)
        cmsswVersion = Tbl(TABLES.CMSSW_VERSION, True)
        
        if self.asc:
            order = "ASC"
        else:
            order = "DESC"


        self.query ="""
        SELECT sub.ds_dataset, sub.rp_proc_version, case sub.ro_reco when 0 then 'Disabled' when 1 then 'Enabled' end ro_reco, sub.ro_cmssw_version, sub.ro_global_tag, sub.ro_config_url, sub.ro_proc_version, case sub.al_alcaskim when 0 then 'Disabled' when 1 then 'Enabled' end al_alcaskim, sub.al_cmssw_version, sub.al_config_url, sub.al_proc_version 
        FROM(
               SELECT
               ds.name ds_dataset,
               rp.proc_version rp_proc_version,
               ro.do_reco ro_reco,
               sw1.name ro_cmssw_version,
               ro.global_tag ro_global_tag,
               ro.config_url ro_config_url,
               ro.proc_version ro_proc_version,
	       al.do_alca al_alcaskim,
	       sw2.name al_cmssw_version,
	       al.config_url al_config_url,
	       al.proc_version al_proc_version
               FROM """ + repackConfig + """ rp, """ + recoConfig + """ ro, """ + alcaConfig  + """ al, """  + cmsswVersion  + """ sw1, """ + cmsswVersion  + """ sw2, """ + primaryDataset  + """ ds
               WHERE rp.run_id = """ + str(self.runid) + """
               AND rp.run_id = ro.run_id AND ro.run_id = al.run_id  AND rp.primary_dataset_id = ro.primary_dataset_id AND ro.primary_dataset_id = al.primary_dataset_id AND ro.cmssw_version_id = sw1.id AND al.cmssw_version_id = sw2.id  AND rp.primary_dataset_id = ds.id
               ORDER BY """ + str(int(self.orderby)+1) + " " + order + """
        ) sub
        """
        
#### 

class RunConfigExpressKeyProvider(TableDataProvider):
    #cols = Cols([Col("Stream"),Col("SplitInProgress"),Col("Proc Version"),Col("Config URL", decorator=buildWebLink),Col("Global tag"),Col("Alcamerge config url", decorator=buildWebLink)])
    cols = Cols([Col("Stream name"),Col("SplitInProgress"),Col("Proc Version"),Col("Config URL", decorator=buildWebLink),Col("Global tag"),Col("Alcamerge config url", decorator=buildWebLink)])
    def __init__(self, runid, orderby=0,asc=True):
	#self.asc= asc
	#self.orderby=orderby
        self.runid = runid
        self.title = "Run " + str(self.runid)
        TableDataProvider.__init__(self,orderby,asc)
        TableDataProvider._load(self)

    def _buildQuery(self):
        expressConfig=Tbl(TABLES.EXPRESS_CONFIG, True)
	streamTable=Tbl(TABLES.STREAM,True)
        if self.asc:
            order = "ASC"
        else:
            order = "DESC"
	
        self.query ="""
	SELECT  st.name, ec.splitInProcessing, ec.proc_version,ec.processing_config_url, ec.global_tag,ec.alcamerge_config_url
	FROM  """ + expressConfig+ """ ec INNER JOIN """+ streamTable +""" st ON st.id = ec.stream_id 
	WHERE ec.run_id=""" + str(self.runid) + """
        ORDER BY  """  + str(int(self.orderby)+1) + """ """ + order
	
	
	
	

class RunsDataProvider(PagedTableDataProvider):
    RUN_ID_TITLE = "Run ID"
    STREAMERS_TITLE = "Streamers"
    REPACKED_TITLE = "Repacked"
    RECO_TITLE = "Reconstructed"
    ALCASKIM_TITLE = "AlcaSkimmed"
    EXPRESS_TITLE = "Express-ed"
    
    VERSION_TITLE = "Version"
    VERSION_EXPRESS_TITLE = "Express"
    VERSION_REPACK_TITLE = "Repack"
    
    cols = Cols([
        Col(RUN_ID_TITLE, decorator=formRunLink),
        Col("Start", decorator=timeToClock),
        Col("End", decorator=timeToClock),
        Col("Process"),
        Col(VERSION_TITLE),
        Col(VERSION_EXPRESS_TITLE),
        Col(VERSION_REPACK_TITLE),
        Col("HLTKey", decorator=buildLeftStrip),
        Col("ACQ_era"),
        Col("Status", info=
            """
                <i style="color:blue;font-size:10px">Active</i> - Run is ongoing and streamer data is still arriving for it<br />
                <i style="color:blue;font-size:10px">CloseOutSegmentInjector</i> - The Tier-0 is trying to make consistent luminosity sections to be repacked (currently we need 4*n streamer files per Luminosity Section)<br />
                <i style="color:blue;font-size:10px">CloseOutScheduler</i> - There is streamer data for the run that has not been assigned to a repack job yet<br />
                <i style="color:blue;font-size:10px">CloseOutRepack</i> - There is streamer data in a run that has not been repacked yet (create repack jobs and wait for them to finish)<br />
                <i style="color:blue;font-size:10px">CloseOutRepackMerge</i> - There is RAW data in the run that needs to be merged (create repack merge jobs and wait from them to finish)<br />
                <i style="color:blue;font-size:10px">CloseOutPromptReco</i> - There is RAW data in the run that needs to be reconstructed (create prompt reco jobs and wait for them to finish)<br />
                <i style="color:blue;font-size:10px">CloseOutPromptRecoMerge</i> - There are RECO data in the run that needs to be merged (create merge jobs and wait for them to finish)<br />
                <i style="color:blue;font-size:10px">CloseOutAlcaSkim</i> - There is RECO data in the run that needs to be AlcaSkimmed (create AlcaSkim jobs and wait for them to finish)<br />
                <i style="color:blue;font-size:10px">CloseOutAlcaSkimMerge</i> - There are ALCARECO data in the run that needs to be merged (create merge jobs and wait for them to finish)<br />
                <i style="color:blue;font-size:10px">Complete</i> - We have finished processing this run (there could have been failures along the way but we've exhausted all automatic retries)
            """
        ),
        Col(STREAMERS_TITLE, info=
            """The number of streamer files"""
        ),
        Col(EXPRESS_TITLE, info=
            """
            The three numbers in the first set represent the number of temporary, final and exported express files.<br><br>
            The second set of numbers represent the process to put files in those states, 1 is 100% based on the available files from the previous step.<br><br>
            The coloured bars show graphically the three processing statuses. Red indicates nothing done, green means processing is complete and yellow is somewhere in between. No bar means nothing is currently expected to be done.
            """
        ),
        Col(REPACKED_TITLE, info=
            """
            The three numbers in the first set represent the number of temporary, final and exported repacked files.<br><br>
            The second set of numbers represent the process to put files in those states, 1 is 100% based on the available files from the previous step.<br><br>
            The coloured bars show graphically the three processing statuses. Red indicates nothing done, green means processing is complete and yellow is somewhere in between. No bar means nothing is currently expected to be done.
            """
        ),
        Col(RECO_TITLE, info=
            """
            The three numbers in the first set represent the number of temporary, final and exported reconstructed files.<br><br>
            The second set of numbers represent the process to put files in those states (1 is 100%) based on the available files from the previous step. This will include files that are not actually processed but acknowledged as such (ie reconstruction is disabled for them).<br><br>
            The coloured bars show graphically the three processing statuses. Red indicates nothing done, green means processing is complete and yellow is somewhere in between. No bar means nothing is currently expected to be done.
            """
        ),
        Col(ALCASKIM_TITLE, info=
            """
            The three numbers in the first set represent the number of temporary, final and exported AlcaSkimmed files.<br><br>
            The second set of numbers represent the process to put files in those states (1 is 100%) based on the available files from the previous step.This will include files that are not actually processed but acknowledged as such (ie AlcaSkim is disabled for them).<br><br>
            The coloured bars show graphically the three processing statuses. Red indicates nothing done, green means processing is complete and yellow is somewhere in between. No bar means nothing is currently expected to be done.
            """
        ),
    ])

    def __init__(self, orderby = 0, asc = True, page = 0, pageSize = 10):
        PagedTableDataProvider.__init__(self, orderby, asc, page, pageSize)
        self.title = "Runs"
        PagedTableDataProvider._load(self)

    def _analysis(self):
        for line in self.data:

	    line[self.cols.getId(self.VERSION_TITLE)]=line[self.cols.getId(self.VERSION_TITLE)].replace("CMSSW_","")
	    line[self.cols.getId(self.VERSION_EXPRESS_TITLE)]=line[self.cols.getId(self.VERSION_EXPRESS_TITLE)].replace("CMSSW_","")
	    line[self.cols.getId(self.VERSION_REPACK_TITLE)]=line[self.cols.getId(self.VERSION_REPACK_TITLE)].replace("CMSSW_","")
		
            runid = line[self.cols.getId(self.RUN_ID_TITLE)]
            numStreamers = line[self.cols.getId(self.STREAMERS_TITLE)]
	    numExpress = line[self.cols.getId(self.STREAMERS_TITLE)+1]
            numExpressMerged = line[self.cols.getId(self.STREAMERS_TITLE)+2]
            numExpressMergedExported = line[self.cols.getId(self.STREAMERS_TITLE)+3]
	    #offset  setted by hand!!! fixit!!!
            numRepacked = line[self.cols.getId(self.REPACKED_TITLE)+2]
            numRepackedMerged = line[self.cols.getId(self.REPACKED_TITLE)+3]
            numReco = line[self.cols.getId(self.REPACKED_TITLE)+4]
	    numRecoMerged = line[self.cols.getId(self.REPACKED_TITLE)+5]
            numAlcaSkimmed = line[self.cols.getId(self.REPACKED_TITLE)+6]
	    numAlcaSkimmedMerged = line[self.cols.getId(self.REPACKED_TITLE)+7]
	    
	    numRepackedMergedExported = line[self.cols.getId(self.REPACKED_TITLE)+8]
	    numRecoMergedExported = line[self.cols.getId(self.REPACKED_TITLE)+9]
            numAlcaSkimmedMergedExported = line[self.cols.getId(self.REPACKED_TITLE)+10]
	    
	    
	    #print """ Streamer: """ +str(numStreamers)+ "  "+str(numExpress)+ "  "+str(numExpressMerged)+ "  "+str(numExpressMergedExported)+"""
	          #"""+ str(numRepacked)+ "  "+str(numRepackedMerged)+ "  "+str(numRepackedMergedExported)
		  
	
	    # analyse express percentage
	    expressP = formatMultiplePercentages([[numExpress, getRunExpressPercentage(runid, numExpressMergedExported), 'Temp'],
	                                          [numExpressMerged, getRunMergePercentage(runid, numExpress, None), 'RAW'],
						  [numExpressMergedExported, getExportedPercentage(numExpressMerged, numExpressMergedExported), 'Exp']
						  ])  

	    # analyse repacked percentage
	    repackedP = formatMultiplePercentages([[numRepacked, getRunRepackedPercentage(runid, numStreamers), 'Temp'],
	                                          [numRepackedMerged, getRunMergePercentage(runid, numRepacked, "RAW"), 'RAW'],
						  [numRepackedMergedExported, getExportedPercentage(numRepackedMerged, numRepackedMergedExported), 'Exp']
						  ])  

	    # analyse reco percentage
	    recoP = formatMultiplePercentages([[numReco, getRunProcessedPercentage(runid, "Reconstructable",numReco), 'Temp'],
	    					[numRecoMerged, getRunMergePercentage(runid, numReco, "RECO"), 'RECO'],
						[numRecoMergedExported, getExportedPercentage(numRecoMerged, numRecoMergedExported), 'Exp']])

            # analyse alcaskim percentage
            alcaSubscription = determineAlcaSubscription(runid)
	    alcaSkimmedP = formatMultiplePercentages([[numAlcaSkimmed, getRunProcessedPercentage(runid, alcaSubscription,numAlcaSkimmed), 'Temp'],
	    					[numAlcaSkimmedMerged, getRunMergePercentage(runid, numAlcaSkimmed,"ALCARECO"), 'ALCA'],
						[numAlcaSkimmedMergedExported, getExportedPercentage(numAlcaSkimmedMerged, numAlcaSkimmedMergedExported), 'Exp']])

	    line[self.cols.getId(self.EXPRESS_TITLE)] = expressP
            line[self.cols.getId(self.REPACKED_TITLE)] = repackedP
            line[self.cols.getId(self.RECO_TITLE)] = recoP
            line[self.cols.getId(self.ALCASKIM_TITLE)] = alcaSkimmedP

	    line = line[:-6] # orig -6

    def _buildCountQuery(self):
        runTable = Tbl(TABLES.RUN)

        self.countQuery = select(
            [func.count(runTable.c.run_id)]
        )

    def _buildMainQuery(self):
        runTable = Tbl(TABLES.RUN, True)
        runStatusTable = Tbl(TABLES.RUN_STATUS, True)
        streamerTable = Tbl(TABLES.STREAMER, True)
	repackStreamerAssocTable = Tbl(TABLES.REPACK_STREAMER_ASSOC, True)
	wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
	wmbsDatasetAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
	datasetTable = Tbl(TABLES.DATASET_PATH, True)
	dataTierTable = Tbl(TABLES.DATA_TIER, True)
	wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
	wmbsSubFilesCompleteTable = Tbl(TABLES.WMBS_SUB_FILES_COMPLETE, True)
	wmbsSubscriptionTable = Tbl(TABLES.WMBS_SUBSCRIPTION, True)
	wmbsSubsTypeTable = Tbl(TABLES.WMBS_SUBS_TYPE, True)
	wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
	wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
	wmbsWorkflowTable = Tbl(TABLES.WMBS_WORKFLOW, True)
        cmsswVersion = Tbl(TABLES.CMSSW_VERSION, True)

        if self.asc: order = "ASC"
        else: order = "DESC"
        def numFileQuery( tier, subscription, run ):
            return """(SELECT COUNT(DISTINCT f.id) 
		FROM """ + wmbsFileDetailsTable + """ f
                        INNER JOIN """ + wmbsDatasetAssocTable  + """ a ON (a.file_id = f.id)
			INNER JOIN """ + datasetTable  + """ dp ON (a.dataset_path_id = dp.id)
                        INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                        INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
		WHERE dp.data_tier = (SELECT id FROM """ + dataTierTable + """ WHERE name = '""" + tier + """')
                      and  m.run = """ + run + """
                      and fsf.fileset = (SELECT id FROM """ + wmbsFilesetTable + """ WHERE name = '""" + subscription + """')
		)"""

        def expFileQuery( tier, run ):
            return """(SELECT  COUNT(DISTINCT f.id)
                FROM """ + wmbsFileDetailsTable + """ f
                        INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                WHERE fsf.fileset = (SELECT id FROM """ + wmbsFilesetTable + """ WHERE name = 'Deletable')
                       AND f.id IN (SELECT DISTINCT f2.id
                                       FROM """ + wmbsFileDetailsTable + """ f2
                                            INNER JOIN """ + wmbsFileRunlumiMapTable + """ m2 ON (f2.id = m2.fileid)
                                            INNER JOIN """ + wmbsFilesetFilesTable + """ fsf2 ON (f2.id = fsf2.fileid)
                                            INNER JOIN """ + wmbsDatasetAssocTable  + """ a ON (a.file_id = f2.id)
                                            INNER JOIN """ + datasetTable  + """ dp ON (a.dataset_path_id = dp.id)
                                       WHERE m2.run = """ + run + """
                                            AND fsf2.fileset = (SELECT id FROM """ + wmbsFilesetTable + """ WHERE name = 'Transferable')
                                            AND dp.data_tier = (SELECT id FROM """ + dataTierTable + """ WHERE name = '""" + tier + """')
                                    )
                )"""
	# special extension for express data!!!
	expressQueries=""" (SELECT COUNT(DISTINCT f.id) 
		FROM """ + wmbsFileDetailsTable + """ f
        	INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
       		 INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
		WHERE 
        		 m.run = sub.run_id
       			 and fsf.fileset = (SELECT id FROM  """ + wmbsFilesetTable + """  WHERE name = 'ExpressMergeable')
			) numExpress,
    
      		 (SELECT COUNT(DISTINCT f.id) 
		FROM """ + wmbsFileDetailsTable + """ f
        	INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
        	INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
		WHERE 
         		m.run = sub.run_id
			and fsf.fileset = (SELECT id FROM  """ + wmbsFilesetTable + """  WHERE name = 'ExpressDBSUploadable')
			) numExpressMerged,
			
		   (SELECT  COUNT(DISTINCT f.id)
     		 FROM """ + wmbsFileDetailsTable + """ f
       		 INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
     		 WHERE fsf.fileset = (SELECT id FROM  """ + wmbsFilesetTable + """  WHERE name = 'Deletable')
        	 AND f.id IN (SELECT DISTINCT f2.id
         		    FROM """ + wmbsFileDetailsTable + """ f2
            		    INNER JOIN """ + wmbsFileRunlumiMapTable + """ m2 ON (f2.id = m2.fileid)
            		    INNER JOIN """ + wmbsFilesetFilesTable + """ fsf2 ON (f2.id = fsf2.fileid)
            			 WHERE m2.run = sub.run_id
               			 AND fsf2.fileset = (SELECT id FROM  """ + wmbsFilesetTable + """  WHERE name = 'ExpressTransferable')
           			 )
     		 ) numExportedExpressMerged,"""
        self.mainQuery = """
            SELECT sub.run_id, sub.start_time, sub.end_time, sub.process, sub.version, sub.expversion, sub.repversion, sub.hltkey, sub.acq_era, sub.status,

            (SELECT COUNT(*) FROM """ + streamerTable + """ s WHERE s.run_id = sub.run_id) numStreamers,
	    """ + expressQueries+"""
            """ + numFileQuery( "RAW", "Mergeable", "sub.run_id" ) + """ numRepacked,

            """ + numFileQuery( "RAW", "DBSUploadable", "sub.run_id" ) + """ numRepackedMerged,

	    """ + numFileQuery( "RECO", "Mergeable", "sub.run_id" ) + """ numReconstructed,

            """ + numFileQuery( "RECO", "DBSUploadable", "sub.run_id" ) + """ numReconstructedMerged,

	    """ + numFileQuery( "ALCARECO", "Mergeable", "sub.run_id" ) + """ numAlcaSkimmed,

	    """ + numFileQuery( "ALCARECO", "DBSUploadable", "sub.run_id" ) + """ numAlcaSkimmedMerged,

            """ + expFileQuery( "RAW", "sub.run_id" ) + """ numExportedRepackedMerged,

            """ + expFileQuery( "RECO", "sub.run_id" ) + """ numExportedReco,

            """ + expFileQuery( "ALCARECO", "sub.run_id" ) + """ numExportedAlcaskim
	 
            FROM(
                SELECT
                r.run_id run_id,
                r.start_time start_time,
                r.end_time end_time,
                r.process process,
                (SELECT name FROM """ + cmsswVersion + """ WHERE id=r.run_version) version,
                (SELECT name FROM """ + cmsswVersion + """ WHERE id=r.express_version) expversion,
                (SELECT name FROM """ + cmsswVersion + """ WHERE id=r.repack_version) repversion,
                r.hltkey hltkey,
                r.acq_era acq_era,
                (SELECT status FROM """ + runStatusTable + """ WHERE id=r.run_status) status
                FROM """ + runTable + """ r
                ORDER BY """ + str(int(self.orderby) + 1) + " " + order + """
            ) sub"""
