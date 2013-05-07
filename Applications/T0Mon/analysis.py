from sqlalchemy import *

import config

from globals import logger

from utils import *
from consts import *
from sqlManager import *

### Analysis module ###
# This module is for functions used for
# analysing table data after executing main query

def getRunRepackedPercentage(runid, numStreamers):
    """
    Get how many percent streamers files were repacked
    """
    assocTable = Tbl(TABLES.REPACK_STREAMER_ASSOC, True)
    streamerTable = Tbl(TABLES.STREAMER, True)

    query = """ SELECT count(distinct a.streamer_id)
		FROM """ + assocTable  + """ a INNER JOIN """ + streamerTable + """ s ON (a.streamer_id = s.streamer_id)
		WHERE s.run_id = :runid"""

    bindvars = { "runid": runid }
    result = executeQuery(query, bindvars)
    numRepack = int(result.fetchone()[0])

    if (numStreamers == 0):
        percentage = 100
    else:
        percentage = numRepack * 100 / numStreamers
    return Percentage(percentage, numRepack )



def getRunExpressPercentage(runid, numExpressMerge):
    """
    Get how many percent streamers files were expressed
    """
    wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
    wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
    wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)

    query = """ SELECT COUNT(fileid)
		FROM """ + wmbsFileRunlumiMapTable + """
		WHERE  run = :runid
		   AND fileid IN (SELECT fileid FROM """ + wmbFilesetFilesTable + """
                                  WHERE fileset = ( SELECT id
                                                       FROM """ + wmbsFilesetTable + """
                                                       WHERE name='ExpressMergeable'
                                                  )

				)
		"""
    bindvars = { "runid": runid}
    result = executeQuery(query, bindvars )
    numStreamersUsedToExpress = int(result.fetchone()[0])

    if (numExpressMerge == 0):
        percentage = 100
    else:
        percentage = numStreamersUsedToExpress * 100 / numExpressMerge
    return Percentage(percentage, numStreamersUsedToExpress)

def getExportedPercentage(numMerged, numMergedExported):
    """
    Get how many percent merged files were exported (every type of file)
    """
    
    if (numMerged == 0):
	percentage = 100
    else:
        percentage = numMergedExported * 100 / numMerged

    return Percentage(percentage, numMergedExported)

def getRunMergePercentage(runid, numToMerge, dataTier):
    """
    Get percentage of files that were merged
    """
    wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
    wmbsDatasetAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
    datasetTable = Tbl(TABLES.DATASET_PATH, True)
    dataTierTable = Tbl(TABLES.DATA_TIER, True)
    wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
    wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
    wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
    wmbsSubscriptionTable = Tbl(TABLES.WMBS_SUBSCRIPTION, True)
    wmbsSubFilesCompleteTable = Tbl(TABLES.WMBS_SUB_FILES_COMPLETE, True)
    if dataTier!=None:
      query = """ SELECT COUNT(DISTINCT f.id)
		FROM """ + wmbsFileDetailsTable + """ f
		   INNER JOIN """ + wmbsDatasetAssocTable  + """ a ON (a.file_id = f.id)
		   INNER JOIN """ + datasetTable  + """ dp ON (a.dataset_path_id = dp.id)
		   INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
		WHERE dp.data_tier = (SELECT id FROM """ + dataTierTable + """ WHERE name = :dataTier )
		   and  m.run = :runid
		   and f.id IN (SELECT fileid FROM """ + wmbsSubFilesCompleteTable + """
                                  WHERE subscription = ( SELECT id
                                                           FROM """ + wmbsSubscriptionTable + """
                                                           WHERE fileset= ( SELECT id
                                                                              FROM """ + wmbsFilesetTable + """
                                                                              WHERE name='Mergeable'
                                                                          )
                                                       )

				)
		"""
      bindvars = { "runid": runid, "dataTier":dataTier }
    else:
      query = """ SELECT COUNT(DISTINCT f.id)
		FROM """ + wmbsFileDetailsTable + """ f
		   INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
		WHERE m.run = :runid
		   and f.id IN (SELECT fileid FROM """ + wmbsSubFilesCompleteTable + """
                                  WHERE subscription = ( SELECT id
                                                           FROM """ + wmbsSubscriptionTable + """
                                                           WHERE fileset= ( SELECT id
                                                                              FROM """ + wmbsFilesetTable + """
                                                                              WHERE name='ExpressMergeable'
                                                                          )
                                                       )

				)
		"""
      bindvars = { "runid": runid }
    result = executeQuery(query, bindvars )
    numMerged = int(result.fetchone()[0])

    if numToMerge == 0:
        percentage = 100
    else:
        percentage = numMerged * 100 / numToMerge

    return Percentage(percentage, numMerged)

def getRunProcessedPercentage(runid, subName, producedFiles):
    """
    Get how many files, marked to be processed, were actually done
    """
    wmbsFileDetailsTable = Tbl(TABLES.WMBS_FILE_DETAILS, True)
    wmbsFileRunlumiMapTable = Tbl(TABLES.WMBS_FILE_RUNLUMI_MAP, True)
    wmbsSubFilesCompleteTable = Tbl(TABLES.WMBS_SUB_FILES_COMPLETE, True)
    wmbsSubscriptionTable = Tbl(TABLES.WMBS_SUBSCRIPTION, True)
    wmbsFilesetTable = Tbl(TABLES.WMBS_FILESET, True)
    wmbsDatasetAssocTable = Tbl(TABLES.WMBS_FILE_DATASET_PATH_ASSOC, True)
    datasetTable = Tbl(TABLES.DATASET_PATH, True)
    wmbsFilesetFilesTable = Tbl(TABLES.WMBS_FILESET_FILES, True)
    dataTierTable = Tbl(TABLES.DATA_TIER, True)

    query = """SELECT COUNT(DISTINCT f.id)
                FROM """ + wmbsFileDetailsTable + """ f
                        INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                        INNER JOIN """ + wmbsSubFilesCompleteTable + """ c ON (f.id = c.fileid)
                WHERE m.run = :runid
                      and c.subscription = (SELECT id
                                              FROM """ + wmbsSubscriptionTable + """
                                              WHERE fileset = (SELECT id
                                                                 FROM """ + wmbsFilesetTable + """
                                                                 WHERE name = :subName
                                                              )
                                           )
            """

    bindvars = { "runid": runid, "subName": subName }
    result = executeQuery(query, bindvars)
    numAlreadyDone = int(result.fetchone()[0])

    query = """SELECT COUNT(DISTINCT f.id)
                FROM """ + wmbsFileDetailsTable + """ f
                 INNER JOIN """ + wmbsFileRunlumiMapTable + """ m ON (f.id = m.fileid)
                 INNER JOIN """ + wmbsFilesetFilesTable + """ fsf ON (f.id = fsf.fileid)
                WHERE m.run = :runid
                 AND fsf.fileset = (SELECT id
                                     FROM """ + wmbsFilesetTable + """
                                     WHERE name = :subName
                                    )
             """

    result = executeQuery(query, bindvars)
    numMarked = int(result.fetchone()[0])

    if (numMarked == 0):
        percentage = 100
    else:
        percentage = numAlreadyDone * 100 / numMarked

    # This is for cases where no files will actually be processed
    if ( numMarked == numAlreadyDone and producedFiles == 0 ):
        numAlreadyDone = 0

    return Percentage(percentage, numAlreadyDone)

class Percentage:
    def __init__(self, percentage, value = None, total = None):
        """
        Parameters:

        percentage -    percentage
        value -         value for percentage
        total -         how much is 100%
        """
        self.percentage = percentage
        self.value = value
        self.total = total

def determineAlcaSubscription( run ):
    """

    _determinaAlcaSubscription_

    Used to figure out which type of subscription is getting used for ALCA

    """

    #return "CombinedAlcaSkimmable"

    query = """SELECT COUNT(fd.id),fs.name FROM wmbs_file_details fd
                  INNER JOIN wmbs_file_runlumi_map rl ON fd.id = rl.fileid
                  INNER JOIN wmbs_fileset_files fsf ON fd.id = fsf.fileid
                  INNER JOIN wmbs_fileset fs ON fs.id = fsf.fileset
                  WHERE rl.run = :runid
                    AND fs.name LIKE '%AlcaSkimmable'
                 GROUP BY fs.name
            """
    bindvars = { "runid": run }
    results = executeQuery( query, bindvars ).fetchall()

    sub = ""
    if len(results) == 0:
        print "No alca subscription found!"
    elif len(results) == 1:
        sub = results[0][1]
    else:
        # find the one with files
        files=0
        foundFiles = False
        for result in results:
            if result[0] > files:
                if foundFiles == True:
                    print "More than one subscription has files, picking most"
                files = result[0]
                sub = result[1]
                foundFiles = True
    return sub
    
