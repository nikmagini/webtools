#!/usr/bin/env python
import sys
import os, pdb
import ConfigParser
from optparse import OptionParser
import Sensor, FillSensorDB
pdb.set_trace()

class AlertsSetup:
  con = ''
  basepath = ''
  #Move these to framework?
  def connectOracle(self, database):
    import cx_Oracle
    cx_Oracle.threaded=True
    self.con = cx_Oracle.connect(database)
    self.cur = cx_Oracle.Cursor(self.con)

  def connectSQLite(self, database):
    from pysqlite2 import dbapi2 as sqlite
    self.con = sqlite.connect(database)
  
  def __init__(self):  
    self.basepath = __file__.replace(__file__.split('/')[-1], '')
    config = ConfigParser.ConfigParser()
    config.read(self.basepath + "alerts.ini")
    database = config.get("SENSORDB", "dbname")
    dbtype = config.get("SENSORDB", "dbtype")
    if dbtype == 'sqlite':
      self.connectSQLite(database)
    elif dbtype == 'oracle':
#      self.connectOracle(database)
      print "Connected to Oracle Alerts"    
#      self.buildSchema()
    else:
      raise 'DB hell'
    
    self.createDB(1)
    
  def buildSchema(self):
    #TODO: Build schema from schema file
    alerts = """create table alert (
	id		number(10) not null,
	metric_id	number(10) not null,
	metric_type	number(10) not null,
	user_id		number(10) not null,
	site_regexp	varchar(100) not null,
	--
	constraint pk_alert primary key (id)
	)"""
   
    alert_pk_seq = """create sequence alert_sq increment by 1 start with 1"""
    self.cur.execute(alerts)
    self.cur.execute(alert_pk_seq)
    
    sql_metrics = """create table sql_metric (
	id		number(10) not null,
	query		varchar(1000) not null,
	name		varchar(100) not null,
	units		varchar(100) not null,
	--
	constraint pk_sql_metric primary key (id),
	constraint uq_sql_metric unique (query)
	)"""

    sql_metric_pk_seq = """create sequence sql_metric_sq increment by 1 start with 1"""    
    self.cur.execute(sql_metrics)
    self.cur.execute(sql_metric_pk_seq)

    metric_types = """create table metric_type (
	metric_table		varchar(1000) not null,
	name		varchar(100) not null,
	--
	constraint uq_metric_type unique (metric_table)
	)"""
    metric_type_pk_seq = """create sequence metric_type_sq increment by 1 start with 1"""
    self.cur.execute(metric_types)
    self.cur.execute(metric_type_pk_seq)
    
    print "Tables and sequences created"
  
    
  def fillDemo(self):
    #TODO: Fill DB with some simple data
    metric = Sensor.Sensor()
    values = metric.getRate("T1_FNAL_MSS","T1_FNAL_Buffer")
    name = "Rate"
    query = """select nvl(sum(done_bytes),0)/1048576/3600 rate from t_history_link_events where timebin >= (sysdate - TO_DATE('01.01.1970:00:00:00','DD.MM.YYYY:HH24:MI:SS'))*24*60*60 - 7200 and to_node = 'T1_FNAL_MSS' and from_node = 'T1_FNAL_Buffer'"""	

    fillDB = FillSensorDB.FillSensorDB() 
    fillDB.Fill_SQL_METRIC(query,name,values)
    return
  
  def createDB(self, demo = None):
    #self.buildSchema()
    #self.con.close()
    print "Closed connection to Oracle Alerts"	
    if demo:
      self.fillDemo()
    return

class CreateConfigFile:
  def __init__(self):  
    self.basepath = __file__.replace(__file__.split('/')[-1], '')
    config = ConfigParser.ConfigParser()
    config.read(self.basepath + "alerts.ini")
    config.add_section('database')
    config.set('database', 'dbname', self.basepath + 'alerts.sqlite')
    config.set('database', 'dbtype', 'sqlite')
    FILE = open('alerts.ini','w')
    config.write(FILE)
    FILE.close() 
     
class InitAlerts:
  def __init__(self):
    parser = OptionParser()
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-i", "--create_ini_file", dest="inifile",
                  help="Create the ini file for SiteDB", action="store_true")

    (options, args) = parser.parse_args()
    if options.inifile:
      ini = CreateConfigFile()
    AlertsSetup()
      
if __name__ == '__main__':

    try:
        alerts = InitAlerts()  
    except:
       	import traceback
       	traceback.print_exc(file = file('trace.txt', 'w'))
