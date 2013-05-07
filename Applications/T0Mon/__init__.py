from time import ctime
from time import time
from subprocess import Popen
import os
#import sys

#from Cheetah.CheetahWrapper import CheetahWrapper
from Framework import Controller
from Framework import templatepage
from Framework.PluginManager import DeclarePlugin

from cherrypy import expose
from cherrypy import request
from cherrypy import response

from dataprovider.runDataProviders import *
from dataprovider.jobDataProviders import *
from dataprovider.fileDataProviders import *
from dataprovider.componentDataProviders import *
#from Templates import index

from guiProvider import *
from utils import *
from consts import *
from historyPages import *

import globals
import config
import sqlManager


class T0Mon (Controller):
    """
    Web page controller
    Provides GUI for user and communicates with backend
    User input should be dealt with only in this class
    """
    
    globals.voidPrint = "This feature is being implemented right now, be patient"
     
    
    def __init__(self, context):
        """
        Init the controller
        """
        Controller.__init__(self, context, __file__)
        # get logger from context
        globals.logger = self.context.Logger()
        # connect to DB
        sqlManager.initBasicConnection()
	
	
	
	
    @expose
    def streamer(self, id, **kwds):
        """
        Display express files history
        """
	page = streamerHistoryPage(self,id, **kwds)
	return str(page)	
################################################################################ Express!	
    @expose
    def express(self, id, **kwds):
        """
        Display express files history
        """
	page = expressHistoryPage(self,id, **kwds)
	return str(page)
    
    @expose
    def expressJob(self, id, **kwds):
        """
        Display express job history
        """
	page = expressJobHistoryPage(self, id, **kwds)
	return str(page)
      
    
    @expose
    def expressMerge(self, id, **kwds):  
        """
        Display express merge files history
        """
	page = expressMergeHistoryPage(self,id, **kwds)
	return str(page)
     
    @expose
    def expressMergeJob(self, id, **kwds): 
        """
        Display express merge job history
        """
	page = expressMergeJobHistoryPage(self,id, **kwds)
	return str(page) 
############################################################################### Repack!
    @expose
    def repack(self, id, **kwds):
        """
        Display repack files history
        """
	page =repackHistoryPage(self,id, **kwds)
	return str(page) 
    
    @expose
    def repackJob(self, id, **kwds):
        """
        Display repack job history
        """
	page = repackJobHistoryPage(self,id, **kwds)
	return str(page) 
    
    @expose
    def repackMerge(self, id, **kwds):
        """
        Display repack merge files history
        """
	page =repackMergeHistoryPage(self,id, **kwds)
	return str(page) 
     
    @expose
    def repackMergeJob(self, id, **kwds):
        """
        Display repack merge files history
        """
	page =repackMergeJobHistoryPage(self,id, **kwds)
	return str(page) 

############################################################################### Reco!
    @expose
    def reco(self, id, **kwds):
        """
        Display reco files history
        """
	page = recoHistoryPage(self,id, **kwds)
        return str(page) 
    
    @expose
    def recoJob(self, id, **kwds):
        """
        Display reco job history
        """
	page =recoJobHistoryPage(self,id, **kwds)
	return str(page) 
    
    @expose
    def recoMerge(self, id, **kwds):
        """
        Display reco merge files history
        """
	page = recoMergeHistoryPage(self,id, **kwds)
        return str(page)
    @expose
    def recoMergeJob(self, id, **kwds):
        """
        Display reco merge files history
        """
	page =recoMergeJobHistoryPage(self,id, **kwds)
        return str(page)

############################################################################### Alcaskim!
    @expose
    def alcaSkim(self, id, **kwds):
        """
        Display alcaSkim files history
        """
	page =alcaSkimHistoryPage(self,id, **kwds)
        return str(page)
    
    @expose
    def alcaSkimJob(self, id, **kwds):
        """
        Display alcaSkim job history
        """
	page =alcaSkimJobHistoryPage(self,id, **kwds)
        return str(page)
    
    @expose
    def alcaSkimMerge(self, id, **kwds):
        """
        Display alcaSkim merge files history
        """
	page =alcaSkimMergeHistoryPage(self,id, **kwds)
        return str(page)
     
    @expose
    def alcaSkimMergeJob(self, id, **kwds):
        """
        Display alcaSkim merge files history
        """
	page =alcaSkimMergeJobHistoryPage(self,id, **kwds)
        return str(page)

################################################################################INDEX


 
    @expose
    def index(self, **kwds):
        """
        Display static page
        """
        globals.pageParams = kwds
        entity = 'static'
	
        if globals.makeStatic:
            globals.makeStatic.poll()

        if os.path.islink( STATIC_PAGE ):
            return self.templatePage (
                "error", {
                'msg': "Bad cache file, please report to <a href=mailto:gowdy@cern.ch>gowdy@cern.ch</a>",
                    "tmplPath" : TMPL_PATH
                }
            )

        # if the page is older than five minutes launch process to generate a new one
        # but don't wait for it to finish
        age = time() - os.path.getmtime( STATIC_PAGE )
        if age > 300 and not os.path.exists( STATIC_LOCK):
            file = open( STATIC_LOCK, 'w')
            file.close()
            if os.path.islink( STATIC_JOB ):
                return self.templatePage (
                    "error", {
                    'msg': "Bad cache generator, please report to <a href=mailto:gowdy@cern.ch>gowdy@cern.ch</a>",
                    "tmplPath" : TMPL_PATH
                    }
                    )
            if not os.path.isdir( STATIC_DIR ) or \
               ( os.path.isdir( STATIC_DIR) and os.path.islink( STATIC_DIR ) ):
                return self.templatePage (
                    "error", {
                    'msg': "Bad cache directory, please report to <a href=mailto:gowdy@cern.ch>gowdy@cern.ch</a>",
                    "tmplPath" : TMPL_PATH
                    }
                    )
            globals.makeStatic = Popen([STATIC_JOB,STATIC_ARGS], cwd = STATIC_DIR )
        #page = index(searchList ={
                    #'entity' : entity + ' ' + str(id),
                    #"staticPage" : STATIC_PAGE
                #})
	#return str(page)
        return self.templatePage (
                "index", {
                    'entity' : entity + ' ' + str(id),
                    "staticPage" : STATIC_PAGE
                }
            )


    @expose
    def jobs(self, **kwds):
        """
        Display jobs for particular run and/or status
        """
        globals.pageParams = kwds
        if globals.pageParams.has_key('table'):
            return self.jobsRepack( **kwds )
        else:
            if globals.pageParams.has_key('inputTier'):
                return self.jobsWMBS( **kwds )
            elif globals.pageParams.has_key('option') \
	                and globals.pageParams['option']=='Express':
		    return self.jobsWMBS( **kwds ) 
            else:
	    	return "<br />No input tier or table name specified"

    def jobsWMBS( self, **kwds ):
        """
        Display information on WMBS jobs
        """
        globals.pageParams = kwds
        error = ""
	if globals.pageParams.has_key('inputTier'):
         inputTier = str(kwds['inputTier'])
         if inputTier != 'RAW' \
            and inputTier != 'RECO' \
            and inputTier != 'ALCARECO':
              error += "<br />Unrecognised input tier"
	else: inputTier=None  #this case is only for ExpressMerge jobs
	
        if globals.pageParams.has_key('mergeFlag'):
            mergeFlag = kwds['mergeFlag']
            if mergeFlag != '!=' and mergeFlag != '=':
                error += "<br />Merge flag in incorrect format"
        else: error += "<br />No status flag specified"
        if globals.pageParams.has_key('status'):
            status = kwds['status']
            if status != "ACQUIRED" and status != "COMPLETE" and status != "FAILED":
                error += "<br />status not valid"
        else: error += "<br />No status flag specified"
        if globals.pageParams.has_key('runid'):
            try:
                runid = int(kwds['runid'])
            except ValueError:
                error += "<br />Run id is not an int"
        else: runid = None

        params = self._getTableParams(T_JOBS)

        if error=="":
            if runid != None:
		if inputTier != None:
                    jtd = WMBSByTierByStatusByRunDP(inputTier, mergeFlag, status, runid, params.orderby, params.asc, params.page)
		else: jtd= ExpressMergeByStatusByRunDP(mergeFlag, status, runid, params.orderby, params.asc, params.page)
            else:
		if inputTier != None:
                   jtd = WMBSByTierByStatusDP(inputTier, mergeFlag, status, params.orderby, params.asc, params.page)
		else: jtd= ExpressMergeByStatusDP(mergeFlag, status, params.orderby, params.asc, params.page)
            jt = getTableGui(T_JOBS, jtd)
        else:
            jt = error

        return self.templatePage("jobs", {
            T_JOBS: jt,
            "time" : ctime(),
            "tmplPath" : TMPL_PATH
        })

    
    
	
    def jobsRepack( self, **kwds):
        globals.pageParams = kwds
        error = ""
        table = str(kwds['table'])
        if globals.pageParams.has_key('status'):
            try:
                status = int(kwds['status'])
            except ValueError:
                error += "<br />Status is not an int"
        else: error += "<br />No status flag specified"
        if globals.pageParams.has_key('runid'):
            try:
                runid = int(kwds['runid'])
            except ValueError:
                error += "<br />Run id is not an int"
        else: runid = None

        params = self._getTableParams(T_JOBS)

        if table != "" and error == "":
	    if table == TABLES.EXPRESS_JOBS:
		if runid != None:
		    jtd = ExpressByStatusByRunDP(status,runid,params.orderby, params.asc, params.page)
		else:
		    jtd = ExpressByStatusDP(status, params.orderby, params.asc, params.page)    
            else: 
             if table == TABLES.REPACK_JOBS:
                if runid != None:
                    jtd = RepackJobByStatusByRunDP(status, runid, params.orderby, params.asc, params.page)
                else:
		    jtd = RepackJobByStatusDP(status, params.orderby, params.asc, params.page)
             else: error += "<br />Bad jobs table name specified"

        if error == "":
            jt = getTableGui(T_JOBS, jtd)
        else:
            jt = error

        return self.templatePage("jobs", {
            T_JOBS: jt,
            "time" : ctime(),
            "tmplPath" : TMPL_PATH
        })

    @expose
    def run(self, runid, **kwds):
        """
        Display run statistics
        """
        globals.pageParams = kwds

        try:
            runid = int(runid)
        except ValueError:
            return self.templatePage ("error", {
                'msg': formatExceptionInfo(),
                "tmplPath" : TMPL_PATH
            })

        params = self._getTableParams(RUN_REPACK_MERGE_T)

	
        try:
            rrmtd = RepackMergeByRunIdDP(runid, params.orderby, params.asc, params.page)
            rrmt = getTableGui(RUN_REPACK_MERGE_T, rrmtd)
        except: rrmt = formatExceptionInfo()

        params = self._getTableParams(RUN_REPACK_T)

        try:
            rrtd = RepackByRunIdDP(runid, params.orderby, params.asc, params.page)
            rrt = getTableGui(RUN_REPACK_T, rrtd)
        except: rrt = formatExceptionInfo()
	
	params = self._getTableParams(RUN_EXPRESS_T)

        try:
            expresstd = ExpressFileByRunDP(runid, params.orderby, params.asc, params.page)
            expressT = getTableGui(RUN_EXPRESS_T, expresstd)
        except: expressT = formatExceptionInfo()
	
	
	params = self._getTableParams(RUN_EXPRESS_MERGE_T)

        try:
            expressMtd = ExpressMergeFileByRunDP(runid, params.orderby, params.asc, params.page)
            expressMT = getTableGui(RUN_EXPRESS_T, expressMtd)
        except: expressMT = formatExceptionInfo()
	

        params = self._getTableParams(RUN_RECO_T)

        try:
            rrtd = RecoByRunIdDP(runid, params.orderby, params.asc, params.page)
            rret = getTableGui(RUN_RECO_T, rrtd)
        except: rret = formatExceptionInfo()

        params = self._getTableParams(RUN_STREAMER_T)

        try:
            rstd = StreamerByRunIdDP(runid, params.orderby, params.asc, params.page)
            rst = getTableGui(RUN_STREAMER_T, rstd)
        except: rst = formatExceptionInfo()

	params = self._getTableParams(RUN_RECO_MERGE_T)

        try:
            rrecomtd = RecoMergeByRunIdDP(runid, params.orderby, params.asc, params.page)
            rrecomt = getTableGui(RUN_RECO_MERGE_T, rrecomtd)
        except: rrecomt = formatExceptionInfo()

        params = self._getTableParams(RUN_ALCASKIM_T)

        try:
            ratd = AlcaskimByRunIdDP(runid, params.orderby, params.asc, params.page)
            rat = getTableGui(RUN_ALCASKIM_T, ratd)
        except: rat = formatExceptionInfo()

        params = self._getTableParams(RUN_ALCASKIM_MERGE_T)

        try:
            ramtd = AlcaskimMergeByRunIdDP(runid, params.orderby, params.asc, params.page)
            ramt = getTableGui(RUN_ALCASKIM_MERGE_T, ramtd)
        except: ramt = formatExceptionInfo()

        try:
            rrstd = RepackStatsDataProvider(runid)
            rrst = getVertTableGui(RUN_REPACK_T, rrstd)
        except: rrst = formatExceptionInfo()

############################## STATS
	try:
            expressStatsTd = ExpressStatsDataProvider(runid)
            expressStatsTd.load()
            expressStatsTable = getVertTableGui(EXPRESS_S_T, expressStatsTd)
        except: expressStatsTable = formatExceptionInfo()
	
	
	try:
            expressMergeStatsTd = StatsByTierDataProvider(None,"Express Merge stats",runid, mergeJobs=True)
	    expressMergeStatsTd.load()
            expressMergeStatsTable = getVertTableGui(RUN_EXPRESS_MERGE_STATS_T, expressMergeStatsTd)
        except: expressMergeStatsTable = formatExceptionInfo()
	
        try:
            rmstd = StatsByTierDataProvider("RAW", "Repack Merge stats", runid, mergeJobs=True)
	    rmstd.load()
            rmst = getVertTableGui(RUN_MERGE_STATS_T, rmstd)
        except: rmst = formatExceptionInfo()

        try:
            rcstd = StatsByTierDataProvider("RAW", "Reco stats", runid)
	    rcstd.load()
            rcst = getVertTableGui(RUN_RECO_STATS_T, rcstd)
        except: rcst = formatExceptionInfo()

        try:
            rrmstd = StatsByTierDataProvider("RECO", "Reco Merge stats", runid,  mergeJobs=True)
            rrmstd.load()
            rrmst = getVertTableGui(RUN_RECO_MERGE_STATS_T, rrmstd)
        except: rrmst = formatExceptionInfo()

        try:
            rastd = StatsByTierDataProvider("RECO", "AlcaSkim stats", runid)
            rastd.load()
            rast = getVertTableGui(RUN_ALCASKIM_STATS_T, rastd)
        except: rast = formatExceptionInfo()

        try:
            rasmtd = StatsByTierDataProvider("ALCARECO", "AlcaSkim Merge stats", runid, mergeJobs=True)
            rasmtd.load()
            rasmt = getVertTableGui(RUN_ALCASKIM_MERGE_STATS_T, rasmtd)
        except: rasmt = formatExceptionInfo()

        try:
            rdtd = RunConfigKeyProvider(runid)
            rdt = getDoubleTableGui(RUN_CONFIG_KEY_T, rdtd)
        except: rdt = formatExceptionInfo()
	
	# Table stream-express_cofig
	params = self._getTableParams(RUN_CONFIG_EXPRESS_KEY_T)
	try:
            rdtde = RunConfigExpressKeyProvider(runid,params.orderby, params.asc)
            rdte = getTableGui(RUN_CONFIG_EXPRESS_KEY_T, rdtde)
        except: rdte = formatExceptionInfo()

        return self.templatePage("run", {
	    RUN_EXPRESS_T: expressT,
	    RUN_EXPRESS_MERGE_T: expressMT,
            RUN_REPACK_T : rrt,
            RUN_RECO_T : rret,
            RUN_RECO_MERGE_T : rrecomt,
            RUN_ALCASKIM_T : rat,
            RUN_ALCASKIM_MERGE_T : ramt,
            RUN_STREAMER_T : rst,
            RUN_REPACK_STATS_T : rrst,
            RUN_MERGE_STATS_T : rmst,
            RUN_RECO_STATS_T : rcst,
	    RUN_RECO_MERGE_STATS_T : rrmst, 
	    RUN_ALCASKIM_STATS_T : rast,
	    RUN_ALCASKIM_MERGE_STATS_T : rasmt,
            RUN_REPACK_MERGE_T : rrmt,
            RUN_CONFIG_KEY_T : rdt,
	    RUN_EXPRESS_STATS_T: expressStatsTable,
	    RUN_EXPRESS_MERGE_STATS_T: expressMergeStatsTable,
	    RUN_CONFIG_EXPRESS_KEY_T : rdte,
            #"streamRepackG" : srg,
            "runid" : runid,
            "time" : ctime(),
            "tmplPath" : TMPL_PATH
        })

    @expose
    def dynamic(self, **kwds):
        """
        Display last runs, job statistics and running jobs
        """

        globals.pageParams = kwds

        # change the default timeout from 300s
        response.timeout = 1200

        #### Components table ####

        try:
            compTableTd = ComponentDataProvider()
            compTable = getTableGui(COMP_T, compTableTd )
        except: compTable = formatExceptionInfo()

        #### Runs table ####
	params = self._getTableParams(RUNS_T)

        try:
            runsTableTd = RunsDataProvider(params.orderby, params.asc, params.page)
            runsTable = getTableGui(RUNS_T, runsTableTd, 100)
        except: runsTable = formatExceptionInfo()
	
	### Express Table ###
	params = self._getTableParams(EXPRESS_T)

        try:
            expressTableTd = ExpressByStatusDP(JOB_NEW, params.orderby, params.asc, params.page,status2=JOB_USED)
            expressTable = getTableGui(EXPRESS_T, expressTableTd, 100)
        except: expressTable = formatExceptionInfo()
	#### Express Merge table ####

        params = self._getTableParams(EXPRESS_MERGE_T)

        try:
            expressMergeTd = ExpressMergeByStatusDP("=", "ACQUIRED", params.orderby, params.asc, params.page)
            expressMergeTable = getTableGui(EXPRESS_MERGE_T, expressMergeTd)
        except: expressMergeTable = formatExceptionInfo()

	### Run Table ###
      

        #### Repacking status table ####

        params = self._getTableParams(REPACKER_T)

        try:
            repackerTd = RepackRunningJobDP(params.orderby, params.asc, params.page)
            repackerTable = getTableGui(REPACKER_T, repackerTd)
        except: repackerTable = formatExceptionInfo()

        #### Reconstruction status table ####

        params = self._getTableParams(RECO_T)

        try:
            recoTd = WMBSByTierByStatusDP("RAW","!=","ACQUIRED",params.orderby, params.asc, params.page)
            recoTable = getTableGui(RECO_T, recoTd)
        except: recoTable = formatExceptionInfo()

        params = self._getTableParams(RECO_MERGE_T)

        try:
            recoMergeTd = WMBSByTierByStatusDP("RECO","=","ACQUIRED",params.orderby, params.asc, params.page)
            recoMergeTable = getTableGui(RECO_MERGE_T, recoMergeTd)
        except: recoMergeTable = formatExceptionInfo()

        #### Merging status table ####

        params = self._getTableParams(MERGE_T)

        try:
            mergeTd = WMBSByTierByStatusDP( "RAW", "=", "ACQUIRED", params.orderby, params.asc, params.page )
            mergeTable = getTableGui(MERGE_T, mergeTd)
        except: mergeTable = formatExceptionInfo()

        #### Alcaskim status tables ####

        params = self._getTableParams(ALCASKIM_T)

        try:
            alcaskimTd = WMBSByTierByStatusDP("ALCARECO","!=","ACQUIRED",params.orderby, params.asc, params.page)
            alcaskimTable = getTableGui(ALCASKIM_T, alcaskimTd)
        except: alcaskimTable = formatExceptionInfo()

        params = self._getTableParams(ALCASKIM_MERGE_T)

        try:
            alcaskimMergeTd = WMBSByTierByStatusDP("ALCARECO","=","ACQUIRED",params.orderby, params.asc, params.page)
            alcaskimMergeTable = getTableGui(ALCASKIM_MERGE_T, alcaskimMergeTd)
        except: alcaskimMergeTable = formatExceptionInfo()
	
	################# Job status Boxes
        self.jobStatus=self._printJobStatusBoxes()

        url = request.base
        if DEV_SERVER in url: dev = True
        else: dev = False

        return self.templatePage("dynamic", dict( self.jobStatus.items() + {
	#return str( dynamic(dict(self.jobStatus.items() + {
            COMP_T : compTable,
            RUNS_T : runsTable,
            REPACKER_T : repackerTable,
	    EXPRESS_T: expressTable,
	    EXPRESS_MERGE_T: expressMergeTable,
            RECO_T : recoTable,
            RECO_MERGE_T : recoMergeTable,
	    ALCASKIM_T : alcaskimTable, 
	    ALCASKIM_MERGE_T : alcaskimMergeTable, 
            MERGE_T : mergeTable,
            "time" : ctime(),
            "dev" : dev,
            "tmplPath" : TMPL_PATH
        }.items()))
	#)
	
	

    #### Private ####
    def _printJobStatusBoxes(self):  # could be merged with an optional parameter runid
        #### Job status tables ######################################################## STATS
	try:
            expressStatsTd = StatsDataProvider("Express stats", TABLES.EXPRESS_JOBS)
            expressStatsTd.load()
            expressStatsTable = getVertTableGui(EXPRESS_S_T, expressStatsTd)
        except: expressStatsTable = formatExceptionInfo()

	try:                     
	    expressMergeStatsTd = StatsByTierDataProvider(None,title="Express Merge stats", mergeJobs=True)
            expressMergeStatsTd.load()
            expressMergeStatsTable = getVertTableGui(EXPRESS_MERGE_S_T, expressMergeStatsTd)
        except: expressMergeStatsTable = formatExceptionInfo()
	
        try:                
            repackStatsTd = StatsDataProvider("Repack stats", TABLES.REPACK_JOBS)
            repackStatsTd.load()
            repackStatsTable = getVertTableGui(REPACK_S_T, repackStatsTd)
        except: repackStatsTable = formatExceptionInfo()

        try:               
	    mergeStatsTd = StatsByTierDataProvider("RAW", "Repack Merge stats", mergeJobs=True)
            mergeStatsTd.load()
            mergeStatsTable = getVertTableGui(MERGE_S_T, mergeStatsTd)
        except: mergeStatsTable = formatExceptionInfo()

        try:
            recoStatsTd = StatsByTierDataProvider("RAW", "Reco stats")
            recoStatsTd.load()
            recoStatsTable = getVertTableGui(RECO_S_T, recoStatsTd)
        except: recoStatsTable = formatExceptionInfo()

        try:
            recoMergeStatsTd = StatsByTierDataProvider("RECO", "Reco Merge stats", mergeJobs=True)
            recoMergeStatsTd.load()
            recoMergeStatsTable = getVertTableGui(RECO_MERGE_S_T, recoMergeStatsTd)
        except: recoMergeStatsTable = formatExceptionInfo()

        try:
            alcaskimStatsTd = StatsByTierDataProvider("ALCARECO", "AlcaSkim stats")
            alcaskimStatsTd.load()
            alcaskimStatsTable = getVertTableGui(ALCASKIM_S_T, alcaskimStatsTd)
        except: alcaskimStatsTable = formatExceptionInfo()

        try:
            alcaskimMergeStatsTd = StatsByTierDataProvider("ALCARECO", "AlcaSkim Merge stats", mergeJobs=True)
            alcaskimMergeStatsTd.load()
            alcaskimMergeStatsTable = getVertTableGui(ALCASKIM_MERGE_S_T, alcaskimMergeStatsTd)
        except: alcaskimMergeStatsTable = formatExceptionInfo()
	return {
	    MERGE_S_T : mergeStatsTable,
            REPACK_S_T : repackStatsTable,
	    EXPRESS_S_T: expressStatsTable,
	    EXPRESS_MERGE_S_T: expressMergeStatsTable,
            RECO_S_T : recoStatsTable,
            RECO_MERGE_S_T : recoMergeStatsTable,
	    ALCASKIM_S_T : alcaskimStatsTable,
	    ALCASKIM_MERGE_S_T : alcaskimMergeStatsTable}
	    
 

    def _getTableParams(self, tableid, orderby = 0, asc = False, page = 0):
        """
        Parse table params from URL
        """
        if globals.pageParams.has_key(tableid + "_p"):
            try:
                pages = globals.pageParams[tableid + "_p"]
                if pages == "all": page = None
                else:
                    page = int(globals.pageParams[tableid + "_p"])
                    if page < 0:
                        page = 0
                        self.context.Logger().error("Page num < 0")
            except ValueError:
                self.context.Logger().error("Could not convert page num to an int")

        if globals.pageParams.has_key(tableid):
            words = globals.pageParams[tableid].rsplit("_")
            try:
                orderby = int(words[0])
                if orderby < 0:
                    orderby = 0
                    self.context.Logger().error("Col id < 0")

            except ValueError:
                self.context.Logger().error("Could not convert table row id to an int")

            if (len(words) == 2):
                if (words[1] == "True"):
                    asc = True
                else: asc = False
            else:
                self.context.Logger().error("Badly formed table params")

        params = TableParams(orderby, asc, page)

        return params

class TableParams:
    """
    Table parameters
    """
    def __init__(self, orderby = 0, asc = False, page = 0):
        """
        Parameters:

        orderby    table ordering column id
        asc        order ascending or descending?
        page       page number to display
        """
        self.orderby = orderby
        self.asc = asc
        self.page = page

# Declare controllers
DeclarePlugin ("/Controllers/" + PROJECT_NAME + "/" + PROJECT_NAME, T0Mon, {"baseUrl": "/" + PROJECT_NAME})

