from Framework.PluginManager import DeclarePlugin
from Framework import Controller, StaticController, templatepage
from cherrypy import expose
import ConfigParser
import sys
import os
import time, calendar, datetime

class Page(Controller):
  title = 'Untitled Alerts Page'
  con = ''

  #Move these to framework?
  def connectOracle(self, database):
    import cx_Oracle
    cx_Oracle.threaded=True
    self.con = cx_Oracle.connect(database)

  def connectSQLite(self, database):
    from pysqlite2 import dbapi2 as sqlite
    self.con = sqlite.connect(self.database)
  
  def __init__(self):
    #Read some config file, get DB connections
    self.basepath = __file__.replace(__file__.split('/')[-1], '')
    config = ConfigParser.ConfigParser()
    config.read(self.basepath + "alerts.ini")
    database = config.get("database", "dbname")
    dbtype = config.get("database", "dbtype")
    if dbtype == 'sqlite':
      self.connectSQLite(database)
    elif dbtype == 'oracle':
      self.connectOracle(database)
    else:
      raise 'DB hell'
    
  def logMessage(self, message):
    #TODO: Move into Bonsai, and do it better
    print " - Alerts :: %s" % message
  
  def getData(self, select = None, binds = None):  
    #Run select SQL query, return dictionary of result
    dataObj = {}
    fields = ''
    if select.lstrip().lower().find("select") == 0:
      if binds == None:
        cur = self.con.execute(select)
        fields = select.replace('select ','').split(' from ', 1)[0].replace(' ', '').split(',')
      else:
        cur = self.con.execute(select, binds)
        fields = binds.keys()
      i = 0
      dataObj = {}
      for row in cur:
        j = 0
        dataObj[i] = {}
        for f in fields:
          dataObj[i][f] = row[j]
          j += 1
        i += 1
    else:
      raise 'Malformed SQL. getData only accepts select statements.'
    return dataObj

  def editData(self, editsql = None, binds = None):
    editsql = editsql.lstrip().lower()
    if editsql.find("update") == 0 or editsql.find("delete") == 0 or editsql.find("insert") == 0:
      return "good query"
    else:
      raise 'Malformed SQL. editData only accepts update, delete and insert statements.'
    #Run update/insert SQL
    return
    
class Alerts(Page):
  def getAlerts(self, select, binds):
    #Connect database
    
    alertlist=''
    return alertlist
  
  def getAlertList(self, id=None):
    if id == None:
      raise "Empty hell"
    elif type(id) != 'int':
      raise "Type hell"
    else:
      #At least id is an integer!
      select = ''
      
  def getMetrics(self):
    type_select = 'select table, name from metric_type'
    type_dict = self.getData(type_select)
    metrics = {}
    for type_row in type_dict:
      metric_select = 'select id, query, name from %s' % type_row['table']
      metric_dict = self.getData(metric_select)
      metrics += {type_row['name']:metric_dict}
    return metrics
  
  def getMetricList(self):
    #TODO: Should this return a list by chopping up getMetrics() or be dropped?
    return getMetrics()
      
  @expose
  def showAlerts(self):
    return self.templatePage ("Alerts_showAlerts",{"alerts":self.getAlertList(id)})

  @expose
  def showMetrics(self):
    return self.templatePage ("Alerts_showMetrics",{"metrics":self.getMetricList()})
  
