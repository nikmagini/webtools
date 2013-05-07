from Framework import templatepage

from dataprovider.runDataProviders import *
from dataprovider.jobDataProviders import *
from dataprovider.fileDataProviders import *
from dataprovider.componentDataProviders import *
##from Templates import index

from guiProvider import *
from utils import *
from consts import *

import globals
import config
import sqlManager

 #this page is the product of a refactoring of the previous huge __init__ source file
 #Every historical page is represented by a class which produces the needed tables in its
 #own order. The methods to build the tables are collected togheter in the generateTable() method.
 
 #The implementations of the data productions are splitted into:
	 #1) jobDataProvider for all the "* job" tables
	 #2) fileDataProvider for all the other tables

##############################################################################################################################
class HistoryPage:
   errMsg= "Not data"
   tableIDs = {T_EXPRESS_JOBS: errMsg, 
	       T_EXPRESS_FILES: errMsg,
	       T_EXPRESS_MERGE_JOBS: errMsg,
	       T_EXPRESS_MERGE_FILES: errMsg,
               T_STREAM_FILES: errMsg,
               T_REPACK_JOBS: errMsg,
               T_REPACK_FILES: errMsg,
               T_MERGE_JOBS: errMsg,
               T_MERGE_FILES: errMsg,
               T_RECO_JOBS: errMsg,
               T_RECO_FILES: errMsg,
               T_RECO_MERGE_JOBS: errMsg,
               T_RECO_MERGE_FILES: errMsg,
               T_ALCA_JOBS: errMsg,
               T_ALCA_FILES: errMsg,
               T_ALCA_MERGE_JOBS: errMsg,
               T_ALCA_MERGE_FILES: errMsg,
	       T_DEPTABLE: errMsg
	       #LSSTYLE:''
	       }
   tableNames ={'eJ':T_EXPRESS_JOBS, 
	       'eF':T_EXPRESS_FILES,
	       'eMJ':T_EXPRESS_MERGE_JOBS,
	       'eMF':T_EXPRESS_MERGE_FILES,
               'st':T_STREAM_FILES,
               'rkJ':T_REPACK_JOBS,
               'rkF':T_REPACK_FILES,
               'rkMJ':T_MERGE_JOBS,
               'rkMF':T_MERGE_FILES,
               'rcJ':T_RECO_JOBS,
               'rcF':T_RECO_FILES,
               'rcMJ':T_RECO_MERGE_JOBS,
               'rcMF':T_RECO_MERGE_FILES,
               'aJ':T_ALCA_JOBS,
               'aF':T_ALCA_FILES,
               'aMJ':T_ALCA_MERGE_JOBS,
               'aMF':T_ALCA_MERGE_FILES}
   def __init__(self, controller, id,entity, **kwds):
	self.entity = entity 
	self.controller = controller
	self.result = None
	self.style=None
	for i in self.tableIDs:
		self.tableIDs[i]=self.errMsg
        globals.pageParams = kwds
	try:
            self.id = int(id)
        except ValueError:
            self.result = self.controller.templatePage (
                "error", {
                    'msg': "Bad " + self.entity + " id",
                    "tmplPath" : TMPL_PATH
                }
            )
	    
   def __buildTreeDepsTable(self, tableTree,start):
	   colspan = 1
	   if (start in tableTree): colspan = len(tableTree[start])
	   printStr = """<b>Table dependancies info:</b><Br/><table><tr> <td COLSPAN=" """+str(colspan)+""" ">"""+ self.tableNames[start]+ "</td></tr>"
	   if (start in tableTree):
	      printStr += "<tr>" 
              for i in tableTree[start]: 
		     cell = self.__DFS(tableTree,i)
		     if len(str(cell))>0:    printStr += "<td>" +str(cell) + "</td>" 
	      printStr+= "</tr>"
	   printStr += "</table>"
	   self.tableIDs[T_DEPTABLE] = printStr
  	   
   def __DFS(self, tableTree,state):
    	if (state not in tableTree):
		 try:  return self.tableNames[state]
		 except: return "" # useful for not complete tree definitions
	else:
		printStr=""
		for i in tableTree[state]: 
		     printStr += "<td>" + self.__DFS(tableTree,i)+ "</td>" 
	        return """<table  ><tr><td colspan=" """+str(len(tableTree[state]))+""" " >"""+ self.tableNames[state]+"</td></tr><tr>"+printStr+"</tr></table>"
 
	   
   def generateTables(self,tableTree,current = None,processedData = None):
       #print str(tableTree[current])+ "  on "+ str(processedData)
       #
       # TO DO: pass to a FUNCTIONAL programming!!!!!!!
       #
       tableName=self.tableNames[current]
       if (processedData==None):
         if (current in tableTree):
	       if debugPrintQueries:
	         self.__buildTreeDepsTable(tableTree,current)
	       else: self.tableIDs[T_DEPTABLE]=""
	       ##################################################### first tables!   
	       #print "STARTER =" +starter
	       params = self.controller._getTableParams(tableName)
	       if current == "st":    ########## streamer
	         try:
            	  currentData = StreamerByIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
		  self.style= currentData.getStyle()
                 except: currentTable = formatExceptionInfo()
	       elif current == "eJ":    ########## expressJob
	         try:
            	  currentData = ExpressJobByJobIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "eF":    ########## expressFiles
	         try:
            	  currentData = ExpressByIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "eMJ":    ########## expressMergeJobs
	         try:
            	  currentData = ExpressMergeJobByIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "eMF":    ########## expressMergeFiles
	         try:
            	  currentData = ExpressMergeByIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "rkJ":    ########## repackJob
	         try:
            	  currentData = RepackJobByJobIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "rkF":    ########## repackJob
	         try:
            	  currentData = RepackByIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "rkMJ":    ########## repackMergeJob 
	         try:
            	  currentData = RepackMergeJobByJobIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "rkMF":    ########## repackMerge 
	         try:
            	  currentData = RepackMergeByIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "rcF":    ########## reco 
	         try:
            	  currentData = RecoByIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "rcJ":    ########## recoJob  
	         try:
            	  currentData = RecoJobByJobIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "rcMJ":    ########## recoMergeJob  
	         try:
            	  currentData = RecoMergeJobByJobIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "rcMF":    ########## recoMerge   
	         try:
            	  currentData = RecoMergeByIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "aJ":    ########## alcaJob   
	         try:
            	  currentData = AlcaSkimJobByJobIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "aMJ":    ########## alca Merge 
	         try:
            	  currentData = AlcaSkimMergeJobByJobIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "aMF":    ########## alca Merge files
	         try:
            	  currentData = AlcaSkimMergeByIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
	       elif current == "aF":    ########## alca 
	         try:
            	  currentData = AlcaSkimByIdsDP([self.id], params.orderby, params.asc, params.page)
            	  currentTable = getTableGui(tableName, currentData)
                 except: currentTable = formatExceptionInfo()
		 
		 ###########################################insert here more first tables
	       else: 
		       currentTable= "Error: "+ current +" first table NOT FOUND!"
		       currentData= None
	       currentTable = wrapInBorder(currentTable)
	       
	 else:  
		 currentTable= "Error: " + current+ " NOT in Tree!" 
	         return
       else:  ## got processed Data
	  (old,sourceData) = processedData
	   ### get parameters
	  params = self.controller._getTableParams(tableName)
	 
	   ### get Ids
	  if sourceData != None:
	    Ids = [int(line[0]) for line in sourceData.data]
	  else: return
	  if (old == '--') and (current== '--' ):
             pass                                                                           ################# streamer
	  
	  #Style: every history page have eihter  Express Data or Repack-Reco-Alca Data
	  #Streamer page has some special queries to choose its style for  every other page the choice is easier: Express->Express, Repack-Reco-Alca-> Bulk
	  #this behavior is saved in the dependancy tree of each page
	  
	  elif ((old == 'st') and (current=='rkJ') and (self.style==None)) or ((old == 'st') and (current=='rkJ') and ('Bulk' in self.style)):
	    try:
              currentData = RepackJobByStreamerIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
 	  elif ((old == 'st') and (current=='eJ') and (self.style==None)) or ((old == 'st') and (current=='eJ') and ('Express' in self.style)):
	    try:
              currentData = ExpressJobByStreamerIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif ((old == 'st') and (current=='eF') and (self.style==None)) or ((old == 'st') and (current=='eF') and ('Express' in self.style)):
	    try:
              currentData = ExpressByStreamerIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif ((old == 'st') and (current=='rkF')and (self.style==None)) or ((old == 'st') and (current=='rkF') and ('Bulk' in self.style)):
	    try:
              currentData = RepackByStreamerIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	                                                                                   ################# express 
	  elif (old == 'eF') and (current=='eMJ') :
	    try:
              currentData = ExpressMergeJobByExpressIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'eF') and (current=='eMF'):
	    try:
              currentData = ExpressMergeByExpressIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
 	  elif (old == 'eF') and (current=='st'):
	    try:
              currentData = StreamerByExpressIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'eF') and (current=='rkMF'):
	    try:
              currentData = RepackMergeByExpressIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	    
          elif (old == 'eJ') and (current== 'st' ):
	    try:
              currentData = StreamerByExpressJobIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'eJ') and (current=='eMJ'):
	    try:
              currentData = ExpressMergeJobByExpressIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  #elif (old == 'eMJ') and (current=='eMF'):
	    #try:
              #currentData = ExpressMergeByExpressIdsDP(Ids, params.orderby, params.asc, params.page)
              #currentTable = getTableGui(tableName, currentData)
            #except: currentTable = formatExceptionInfo()
          elif (old == 'eMJ') and (current=='eF'):
	    try:
              currentData = ExpressByExpressMergeJobIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'eMF') and (current=='eF'):
	    try:
              currentData = ExpressByExpressMergeIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'eMF') and (current=='eMJ'):
	    try:
              currentData = ExpressMergeJobByExpressMergeIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()

	                                                                            ################# repack
	  elif (old == 'rkF') and (current=='rkMJ'):
	    try:
              currentData = RepackMergeJobByRepackIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
 	  elif (old == 'rkF') and (current=='rkJ'):
	    try:
              currentData = RepackJobByRepackIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
                                                                    
	  elif (old == 'rkF') and (current=='rkMF'):
	    try:
              currentData = RepackMergeByRepackIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
 	  elif (old == 'rkJ') and (current=='st'):
	    try:
              currentData = StreamerByRepackJobIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'rkMF') and (current=='rcJ'):
	    try:
              currentData = RecoJobByMergeIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'rkMF') and (current=='rcF'):
	    try:
              currentData = RecoByMergeIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
 	  elif (old == 'rkMF') and (current=='rkMJ'):
	    try:
              currentData = RepackMergeJobByRepackMergeIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
 	  elif (old == 'rkMF') and (current=='rcJ'):
	    try:
              currentData = RecoJobByMergeIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	 
 	  elif (old == 'rkMF') and (current=='rkF'):
	    try:
              currentData = RepackByRepackMergeIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	    
          elif (old == 'rkMJ') and (current=='rcJ'):
	    try:
              currentData = RecoJobByRecoIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
          elif (old == 'rkMJ') and (current=='rkF'):
	    try:
              currentData = RepackByRepackMergeJobIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  
 	  elif (old == 'rcJ') and (current=='rkMF'):                           ################# reco
	    try:
              currentData = RepackMergeByRecoJobIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo() 
	  elif (old == 'rcF') and (current=='rcMJ'):        
	    try:
              currentData = RecoMergeJobByRecoIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'rcF') and (current=='rcMF'):
	    try:
              currentData = RecoMergeByRecoIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'rcF') and (current=='rcJ'):
	    try:
              currentData = RecoJobByRecoIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'rcF') and (current=='rkMF'): 
	    try:
              currentData = RepackMergeByRecoIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'rcF') and (current=='aJ'):
	    try:
              currentData = AlcaSkimJobByRecoIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'rcF') and (current=='aF'): 
	    try:
              currentData = AlcaSkimByRecoMergeIdsDp(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  #elif (old == 'rcMF') and (current=='aJ'):
	    #try:
              #currentData = AlcaSkimJobByRecoMergeIdsDP(Ids, params.orderby, params.asc, params.page)
              #currentTable = getTableGui(tableName, currentData)
            #except: currentTable = formatExceptionInfo()
	  elif (old == 'rcMJ') and (current=='rcF'):
	    try:
              currentData = RecoByRecoMergeJobIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'rcMF') and (current=='rcF'):
	    try:
              currentData = RecoByRecoMergeIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'rcMF') and (current=='rcMJ'):
	    try:
              currentData = RecoMergeJobByRecoMergeIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  #elif (old == 'rcMF') and (current=='aF'):                          ################# alca
	    #try:
              #currentData = AlcaSkimByRecoMergeIdsDp(Ids, params.orderby, params.asc, params.page)
              #currentTable = getTableGui(tableName, currentData)
            #except: currentTable = formatExceptionInfo()
	  elif (old == 'aF') and (current=='aMF'):
	    try:
              currentData = AlcaSkimMergeByAlcaSkimIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'aF') and (current=='aMJ'):
	    try:
              currentData = AlcaSkimMergeJobByAlcaSkimIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'aF') and (current=='rcMF'):
	    try:
              currentData = RecoMergeByAlcaSkimIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'aF') and (current=='aJ'): 
	    try:
              currentData = AlcaSkimJobByAlcaSkimIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'aJ') and (current=='rcF'):
	    try:
              currentData = RecoByAlcaSkimJobIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'aMJ') and (current=='aF'):                            ###########to Implement
	    try:
              currentData = AlcaSkimByAlcaSkimMergeJobIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'aMJ') and (current=='aMF'):
	    try:
              currentData = AlcaSkimMergeByAlcaSkimMergeIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'aMF') and (current=='aMJ'):
	    try:
              currentData = AlcaSkimMergeJobByAlcaSkimMergeIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	  elif (old == 'aMF') and (current=='aF'):
	    try:
              currentData = AlcaSkimByAlcaSkimMergeIdsDP(Ids, params.orderby, params.asc, params.page)
              currentTable = getTableGui(tableName, currentData)
            except: currentTable = formatExceptionInfo()
	    
	    
	    ########################################insert here more tables dependancies
	  else: 
		 currentTable= "The dependancy: "+ self.tableNames[current] + " <br /> from " +self.tableNames[old]+ " is NOT IMPLEMENTED "
		 #if self.style != None currentTable+=" <br /> Style: " + "".join(self.style)
		 if self.style!=None: currentTable= self.errMsg 
		 currentData=None
	    
	####### saving results
       self.tableIDs[tableName]=currentTable
       	 ##### recursive Calling 
       if (current in tableTree):
         for i in tableTree[current]:
	    #print "calling "+ i 
	    if i in self.tableNames.keys() and  'currentData' in locals():
	      self.generateTables(tableTree,i,(current,currentData))
       
       return
	 
	       
################################################################################################################### streamer 
class streamerHistoryPage(HistoryPage):
	
    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'Streamer', **kwds)
	    if self.result == None:
	       self.__buildPage()
	    
    def __buildPage(self):
	tableTree = {'st': ['eJ','eF','rkJ','rkF'],
	             'eF':['eMJ','eMF'],
		     #'eMJ': ['eMF'],
		     'rkF': ['rkMJ','rkMF'],
		     'rkMF': ['rcJ', 'rcF'],
		     'rcF': ['rcMF', 'rcMJ','aJ','aF'],
		     #'rcF':['aF'],
		     'aF': ['aMJ','aMF']
             } 
	self.generateTables(tableTree,'st',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))

       
    def __str__(self):
	return self.result

  
	
#####################################################################################################################     expressJob	
class expressJobHistoryPage(HistoryPage):
	
    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'Express job', **kwds)
	    if self.result == None:
	       self.__buildPage()
	    
    def __buildPage(self):
	tableTree = {'eJ': ['st'],
             'st': [ 'eF'], # 'rkJ','rkF'],
             'eF': ['eMJ', 'eMF']
             #'rkF': ['rkMF','rkMJ'],
             #'rkMF': ['rcJ','rcF'],
             #'rcF': ['rcMJ','rcMF'],
	     #'rcMF': ['aJ','aF'],
	     #'aF': ['aMF','aMJ']
	     } 
	self.generateTables(tableTree,'eJ',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))

       
    def __str__(self):
	return self.result


class expressHistoryPage(HistoryPage):

    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'Express Files', **kwds)
	    if self.result == None:
	       self.__buildPage()
	
    def __buildPage(self):
	tableTree = {'eF': ['st','eMF','eMJ'], #,'rkMF'],
             'st': ['eJ']
             #'eJ': ['eMJ']
             #'rkMF': ['rkF','rkMJ','rcJ','rcF'],
	     #'rkF':['rkJ'],
	     #'rcF':['rcMF','rcMJ'],
	     #'rcMF': ['aJ','aF'],
	     #'aF': ['aMJ','aMF']
             } 
	self.generateTables(tableTree,'eF',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))
	    
    def __str__(self):
	return self.result
    
class expressMergeHistoryPage(HistoryPage):

    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'Express Merge Files', **kwds)
	    if self.result == None:
	       self.__buildPage()
	
    def __buildPage(self):
	tableTree = {'eMF': ['eF','eMJ'],
	             'eF':['st'],
		     'st': ['eJ'] #,'rkJ','rkF'],
		     #'rkF': ['rkMJ','rkMF'],
		     #'rkMF': ['rcJ', 'rcF'],
		     #'rcF': ['rcMF', 'rcMJ'],
		     #'rcMF':['aJ','aF'],
		     #'aF': ['aMJ','aMF']
             } 
	self.generateTables(tableTree,'eMF',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))
	    
    def __str__(self):
	return self.result
	
	

class expressMergeJobHistoryPage(HistoryPage):

    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'Express Merge jobs', **kwds)
	    if self.result == None:
	       self.__buildPage()
	
    def __buildPage(self):
	tableTree = {'eMJ':['eF'],
		     'eF':['st','eMF'],
		     'st': ['eJ'] #,'rkJ','rkF'],
		     #'rkF': ['rkMJ','rkMF'],
		     #'rkMF': ['rcJ', 'rcF'],
		     #'rcF': ['rcMF', 'rcMJ'],
		     #'rcMF':['aJ','aF'],
		     #'aF': ['aMJ','aMF']
             } 
	self.generateTables(tableTree,'eMJ',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))
	    
    def __str__(self):
	return self.result
######################################################################################################################################repack
class repackHistoryPage(HistoryPage):
	
    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'Repack job', **kwds)
	    if self.result == None:
	       self.__buildPage()
	    
    def __buildPage(self):
	tableTree = {'rkF': ['rkJ','rkMJ','rkMF'],
	      'rkJ': ['st'],
             #'st': [ 'eF','eJ'],
             #'eF': ['eMJ', 'eMF'],
             'rkMF': ['rcJ','rcF'],
             'rcF': ['rcMJ','rcMF','aJ','aF'],
	     #'rcMF': ['aF'],
	     'aF': ['aMF','aMJ']} 
	self.generateTables(tableTree,'rkF',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))

       
    def __str__(self):
	return self.result
    
    
class repackJobHistoryPage(HistoryPage):
	
    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'Repack job', **kwds)
	    if self.result == None:
	       self.__buildPage()
	    
    def __buildPage(self):
	tableTree = {'rkJ': ['st'],
             'st': ['rkF'], #'eF','eJ'],
             #'eF': ['eMJ', 'eMF'],
             'rkF': ['rkMF','rkMJ'],
             'rkMF': ['rcJ','rcF'],
             'rcF': ['rcMJ','rcMF','aJ','aF'],
	     'aF': ['aMF','aMJ']} 
	self.generateTables(tableTree,'rkJ',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))

       
    def __str__(self):
	return self.result
 
    
class repackMergeJobHistoryPage(HistoryPage):
	
    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'Repack Merge job', **kwds)
	    if self.result == None:
	       self.__buildPage()
	    
    def __buildPage(self):
	tableTree = {'rkMJ': ['rkF'],
	     'rkF':['rkJ','rkMF'],
	     'rkJ':['st'],
             #'st': [ 'eF','eJ'],
             #'eF': ['eMJ', 'eMF'],
             'rkMF': ['rcJ','rcF'],
             'rcF': ['rcMJ','rcMF','aJ','aF'],
	     'aF': ['aMF','aMJ']} 
	self.generateTables(tableTree,'rkMJ',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))

       
    def __str__(self):
	return self.result
        
class repackMergeHistoryPage(HistoryPage):
	
    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'Repack Merge files', **kwds)
	    if self.result == None:
	       self.__buildPage()
	    
    def __buildPage(self):
	tableTree = {'rkMF': ['rkF','rkMJ','rcJ','rcF'],
	     'rkF':['rkJ'],
	     'rkJ':['st'],
             #'st': [ 'eF','eJ'],
             #'eF': ['eMJ', 'eMF'],
             'rcF': ['rcMJ','rcMF','aJ','aF'],
	     'aF': ['aMF','aMJ']} 
	self.generateTables(tableTree,'rkMF',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))

       
    def __str__(self):
	return self.result
    
##################################################################################################################### reco
class recoHistoryPage(HistoryPage):
	
    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'Reco files', **kwds)
	    if self.result == None:
	       self.__buildPage()
	    
    def __buildPage(self):
	tableTree = {'rcF': ['rcJ','rkMF','rcMF','rcMJ','aJ','aF'],
             #'st': [ 'eF','eJ'],
             'rkMF': ['rkMJ','rkF'],
	     'rkF':['rkJ'],
	     'rkJ':['st'],
	     #'eF':['eMF','eMJ'],
	     'aF': ['aMF','aMJ']} 
	self.generateTables(tableTree,'rcF',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))

       
    def __str__(self):
	return self.result

class recoJobHistoryPage(HistoryPage):
	
    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'Reco jobs', **kwds)
	    if self.result == None:
	       self.__buildPage()
	    
    def __buildPage(self):
	tableTree = {'rcJ': ['rkMF'],
             'rkMF': [ 'rkF','rkMJ', 'rcF'],
             'rkF': ['rkJ'],
	     'rkJ':['st'],
	     #'st':['eJ','eF'],
	     #'eF':['eMF','eMJ'],
	     'rcF':['rcMJ','rcMF','aJ','aF'],
	     #'rcMF':['aF'],
	     'aF': ['aMF','aMJ']} 
	self.generateTables(tableTree,'rcJ',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))

       
    def __str__(self):
	return self.result

 

class recoMergeJobHistoryPage(HistoryPage):
	
    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'Reco Merge jobs', **kwds)
	    if self.result == None:
	       self.__buildPage()
	    
    def __buildPage(self):
	tableTree = {'rcMJ': ['rcF'],
             'rcF': [ 'aJ','rcMF','rcJ','aF'],
             #'rcMF': [],
	     'rcJ':['rkMF'],
	     #'st':['eJ','eF'],
	     #'eF':['eMF','eMJ'],
	     'rkMF':['rkMJ','rkF'],
	     'rkF':['rkJ'],
	     'rkJ':['st'],
	     'aF': ['aMF','aMJ']} 
	self.generateTables(tableTree,'rcMJ',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))

       
    def __str__(self):
	return self.result

 

class recoMergeHistoryPage(HistoryPage):
	
    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'Reco Merge files', **kwds)
	    if self.result == None:
	       self.__buildPage()
	    
    def __buildPage(self):
	tableTree = {'rcMF': ['rcF','rcMJ'],
             'rcF': [ 'aJ','rkMF','rcJ','aF'],
             'rkMF': ['rkF','rkMJ'],
	     'rkF':['rkJ'],
	     #'st':['eJ','eF'],
	     #'eF':['eMF','eMJ'],
	     'aF': ['aMF','aMJ'],
	     'rkJ':['st']
	      } 
	self.generateTables(tableTree,'rcMF',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))

       
    def __str__(self):
	return self.result
 ################################################################################################## alcaSkim
 
 

class alcaSkimJobHistoryPage(HistoryPage):
	
    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'alcaSkim jobs', **kwds)
	    if self.result == None:
	       self.__buildPage()
	    
    def __buildPage(self):
	tableTree = {'aJ': ['rcF'],
             'rcF': ['rcMJ', 'rcMF','aF','rkMF','rcJ'],
	     'aF':['aMF','aMJ'],
	     'rkMF': ['rkMJ','rkF'],
	     'rkF':['rkJ'],
	     'rkJ':['st'],
             #'rcMJ': ['rcF'],
	     #'rcF':['rcJ'],
	     #'rcJ':['rkMF'],
	     #'rkMF':['rkMJ','rkF'],
	     #'rkF':['rkJ'],
	     #'rkJ': ['st'],
	     ##'st':['eJ','eF'],
	     ##'eF':['eMF','eMJ']
	     } 
	self.generateTables(tableTree,'aJ',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))

       
    def __str__(self):
	return self.result
    
    

class alcaSkimHistoryPage(HistoryPage):
	
    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'alcaSkim files', **kwds)
	    if self.result == None:
	       self.__buildPage()
	    
    def __buildPage(self):
	tableTree = {'aF': ['aJ','aMJ','aMF'],
	     'aJ':['rcF'],
             'rcMF': ['rcMJ'],
	     'rcF':['rcJ','rkMF','rcMF'],
	     'rkMF':['rkMJ','rkF'],
	     'rkF':['rkJ'],
	     'rkJ': ['st'],
	     #'st':['eJ','eF'],
	     #'eF':['eMF','eMJ']
	     } 
	self.generateTables(tableTree,'aF',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))

       
    def __str__(self):
	return self.result
    
    
 

class alcaSkimMergeJobHistoryPage(HistoryPage):
	
    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'alcaSkim Merge jobs', **kwds)
	    if self.result == None:
	       self.__buildPage()
	    
    def __buildPage(self):
	tableTree = {'aMJ': ['aF'],
             'aF': ['aJ','aMF'],
	     'aJ':['rcF'],
	     'rcF':['rcMJ','rcMF','rcJ'],
	     #'rcMJ':['rcF'],
	     #'rcF': ['rcJ'],
	     'rcJ':['rkMF'],
	     'rkMF':['rkMJ','rkF'],
	     'rkF': ['rkJ'],
	     'rkJ': ['st'],
	     #'st':['eJ','eF'],
	     #'eF':['eMF','eMJ']
	     } 
	self.generateTables(tableTree,'aMJ',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))

       
    def __str__(self):
	return self.result
    


class alcaSkimMergeHistoryPage(HistoryPage):
	
    def __init__(self,controller, id, **kwds):
	    HistoryPage.__init__(self,controller, id,'alcaSkim Merge files', **kwds)
	    if self.result == None:
	       self.__buildPage()
	    
    def __buildPage(self):
	tableTree = {'aMF': ['aMJ','aF'],
             'aF': ['aJ'],
	     'aJ':['rcF'],
	     'rcF':['rcMJ','rcMF','rcJ','rkMF'],
	     #'rcF': [],
	     'rkMF':['rkMJ','rkF'],
	     'rkF': ['rkJ'],
	     'rkJ': ['st'],
	     #'st':['eJ','eF'],
	     #'eF':['eMF','eMJ']
	     } 
	self.generateTables(tableTree,'aMF',None)
	#print str(self.tableIDs)
	self.result= self.controller.templatePage(
                "history", dict(self.tableIDs.items()+{
                    'entity' : self.entity + ' ' + str(id),
                    "tmplPath" : TMPL_PATH
                }.items()
            ))

       
    def __str__(self):
	return self.result
    
  