import config
import os

PROJECT_NAME = 'T0Mon'


# Table IDs
COMP_T = 'compT'
RUNS_T = 'runsT'
EXPRESS_MERGE_S_T = 'expressMergeST'
EXPRESS_S_T = 'expressST'
EXPRESS_T = 'expressT'
EXPRESS_MERGE_T = "expressMergeT"
REPACKER_T = 'repackerT'
REPACK_S_T = 'repackST'
MERGE_T = 'mergeT'
MERGE_S_T = 'mergeST'
RECO_T = 'recoT'
RECO_MERGE_T = 'recoMergeT'
RECO_S_T = 'recoST'
RECO_MERGE_S_T = 'recoMergeST'
ALCASKIM_T = 'alcaskimT'
ALCASKIM_MERGE_T = 'alcaskimMergeT'
ALCASKIM_S_T = 'alcaskimST'
ALCASKIM_MERGE_S_T = 'alcaskimMergeST'
RUN_EXPRESS_T = 'runExpressT'
RUN_EXPRESS_MERGE_T = 'runExpressMergeT' 
RUN_REPACK_T = 'runRepackT'
RUN_CONFIG_KEY_T = 'runConfigKeyT'
RUN_CONFIG_EXPRESS_KEY_T = 'runConfigExpressKeyT'
RUN_REPACK_MERGE_T = 'runRepackMergeT'
RUN_RECO_T = 'runRecoT'
RUN_RECO_MERGE_T = 'runRecoMergeT'
RUN_ALCASKIM_T = 'runAlcaskimT'
RUN_ALCASKIM_MERGE_T = 'runAlcaskimMergeT'
RUN_STREAMER_T = 'runStreamerT'
RUN_REPACK_STATS_T = 'runRepackStatsT'
RUN_MERGE_STATS_T = 'runMergeStatsT'
RUN_RECO_STATS_T = 'runRecoStatsT'
RUN_EXPRESS_STATS_T ='runExpressStatsT'
RUN_EXPRESS_MERGE_STATS_T = 'runExpressMergeStatsT'
RUN_RECO_MERGE_STATS_T = 'runRecoMergeStatsT'
RUN_ALCASKIM_STATS_T = 'runAlcaskimStatsT'
RUN_ALCASKIM_MERGE_STATS_T = 'runAlcaskimMergeStatsT'

T_STREAM_FILES = 'streamerFiles'
T_EXPRESS_JOBS = 'expressJobs'
T_EXPRESS_FILES = 'expressFiles'
T_EXPRESS_MERGE_JOBS= 'expressMergeJobs'
T_EXPRESS_MERGE_FILES='expressMergeFiles'
T_RECO_FILES = 'recoFiles'
T_RECO_JOBS = 'recoJobs'
T_REPACK_FILES = 'repackFiles'
T_REPACK_JOBS = 'repackJobs'
T_MERGE_FILES = 'mergeFiles'
T_MERGE_JOBS = 'mergeJobs'
T_RECO_MERGE_JOBS = 'recoMergeJobs'
T_RECO_MERGE_FILES = 'recoMergeFiles'
T_ALCA_JOBS = 'alcaJobs'
T_ALCA_FILES = 'alcaFiles'
T_ALCA_MERGE_JOBS = 'alcaMergeJobs'
T_ALCA_MERGE_FILES = 'alcaMergeFiles'

T_JOBS = 'jobs'
T_DEPTABLE = 'depTable'

#LSSTYLE='sStyle'
# Identify cheetah template full path
TMPL_PATH = os.path.join(__file__.rsplit ("/", 1)[0], "Templates/")

# Place to put get static page
STATIC_JOB = os.path.join(__file__.rsplit ("/", 1)[0], "cron/makeStatic")
STATIC_DIR = os.environ["PROJ_DIR"] + "/var/"
STATIC_PAGE = STATIC_DIR + "T0Mon.static"
STATIC_LOCK = STATIC_DIR + "T0Mon.lock"
STATIC_ARGS = os.environ['T0MON_PORT']+'/'+os.environ['T0MON_BASE']





REPACK_RECONSTRUCTION_QUEUED = 5
REPACK_RECONSTRUCTION_DISABLED = 6

RECONSTRUCTED_ALCASKIM_QUEUED = 6
RECONSTRUCTED_ALCASKIM_DISABLED = 7

RECONSTRUCTED_RECO = "RECO"
RECONSTRUCTED_ALCASKIM = "ALCARECO"

class TABLES:
    PREFIX = ""

    MERGE_JOBS = PREFIX + 'merge_job_def'
    RECO_JOBS = PREFIX + 'promptreco_job_def'
    REPACK_JOBS = PREFIX + 'repack_job_def'
    EXPRESS_JOBS= PREFIX + 'express_job_def'
    ALCA_JOBS = PREFIX + 'alcaskim_job_def'

    RUN = PREFIX + 'run'
    RUN_STATUS = PREFIX + 'run_status'
    STREAMER = PREFIX + 'streamer'
    STREAM = PREFIX + 'stream'
    REPACKED = PREFIX + 'repacked'
    REPACK_STREAMER_ASSOC = PREFIX + 'repack_streamer_assoc'
    MERGE_JOB_REPACK_ASSOC = PREFIX + 'merge_job_repack_assoc'
    MERGE_JOB_RECO_ASSOC = PREFIX + 'merge_job_reco_assoc'
    RECO_JOB_REPACK_ASSOC = PREFIX + 'promptreco_job_repack_assoc'
    ALCA_JOB_RECO_ASSOC = PREFIX + 'alcaskim_job_reco_assoc'
    JOB_DATASET_STREAMER_ASSOC = PREFIX + 'repack_job_streamer_assoc'
    EXPRESS_JOB_STREAMER_ASSOC = PREFIX + 'express_job_streamer_assoc'
    REPACK_STREAMER_ASSOC = PREFIX + 'repack_streamer_assoc'
    JOB_STATUS = PREFIX + 'job_status'
    PRIMARY_DATASET = PREFIX + 'primary_dataset'
    EXPORT_STATUS = PREFIX + 'export_status'
    REPACKED_STATUS = PREFIX + 'repacked_status'
    RECONSTRUCTED = PREFIX + 'reconstructed'
    RECONSTRUCTED_STATUS = PREFIX + 'reconstructed_status'
    REPACKED_RECO_PARENTAGE = PREFIX + 'repacked_reco_parentage'
    RECO_MERGE_PARENTAGE = PREFIX + 'reco_merge_parentage'
    ALCASKIM_MERGE_PARENTAGE = PREFIX + 'alcaskim_merge_parentage'
    REPACKED_MERGE_PARENTAGE = PREFIX + 'repacked_merge_parentage'
    EXPORT_STATUS = PREFIX + 'export_status'
    VERSION = PREFIX + 'version'

    REPACK_CONFIG = PREFIX + 'repack_config'
    RECO_CONFIG = PREFIX + 'reco_config'
    CMSSW_VERSION = PREFIX + 'cmssw_version'
    ALCA_CONFIG = PREFIX + 'alca_config'

    WMBS_FILE_DETAILS = PREFIX + 'wmbs_file_details'
    WMBS_FILE_DATASET_PATH_ASSOC = PREFIX + 'wmbs_file_dataset_path_assoc'
    DATASET_PATH = PREFIX + 'dataset_path'
    DATA_TIER = PREFIX + 'data_tier'
    DATASET_RUN_STREAM_ASSOC = PREFIX + 'dataset_run_stream_assoc'
    PROCESSED_DATASET = PREFIX + 'processed_dataset'
    WMBS_FILE_RUNLUMI_MAP = PREFIX + 'wmbs_file_runlumi_map'
    WMBS_SUB_FILES_COMPLETE = PREFIX + 'wmbs_sub_files_complete'
    WMBS_SUB_FILES_ACQUIRED = PREFIX + 'wmbs_sub_files_acquired'
    WMBS_SUBSCRIPTION = PREFIX + 'wmbs_subscription'
    WMBS_SUBS_TYPE = PREFIX + 'wmbs_subs_type'
    WMBS_FILESET = PREFIX + 'wmbs_fileset'
    WMBS_FILESET_FILES = PREFIX + 'wmbs_fileset_files' 
    WMBS_FILE_PARENT = PREFIX + 'wmbs_file_parent'
    WMBS_WORKFLOW = PREFIX + 'wmbs_workflow'

    WMBS_JOB = PREFIX + 'wmbs_job'
    WMBS_JOB_STATE = PREFIX + 'wmbs_job_state'
    WMBS_JOBGROUP = PREFIX + 'wmbs_jobgroup'
    WMBS_GROUP_JOB_COMPLETE = PREFIX + 'wmbs_group_job_complete'
    WMBS_GROUP_JOB_ACQUIRED = PREFIX + 'wmbs_group_job_acquired'
    WMBS_GROUP_JOB_FAILED = PREFIX + 'wmbs_group_job_failed'
    WMBS_JOB_ASSOC = PREFIX + 'wmbs_job_assoc'

    COMPONENT_HEARTBEAT = PREFIX + 'component_heartbeat'
    
    EXPRESS_CONFIG = PREFIX + 'express_config'

JOB_NEW, JOB_USED, JOB_SUCCESS, JOB_FAILURE = range(1, 5)

JOB_STATUS = {
    "ACQUIRED": "acquired",
    "COMPLETE": "successful",
    "FAILED": "failed",
}

JOB_TYPE = {
    "RAW": {
             "=": "Repack merge",
             "!=": "Reconstruction"
           },
    "RECO": { 
              "=": "Reco merge",
              "!=": "AlcaSkim"
            },
    "ALCARECO": { 
                  "=": "AlcaSkim merge",
                  "!=": "AlcaSkim"
                }
}

JOB_STATUS_REPACKED = {
    JOB_NEW : "new",
    JOB_USED: "used",
    JOB_SUCCESS: "successful",
    JOB_FAILURE: "failed",
}

DEV_SERVER = 'vocms13'
