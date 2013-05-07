import sys
import os, pdb
import ConfigParser
from optparse import OptionParser

class FillSensorDB:

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
    		con = ''
    		cursor = ''
    		basepath = ''
    		#Move these to framework?
    		self.basepath = __file__.replace(__file__.split('/')[-1], '')
    		config = ConfigParser.ConfigParser()
    		config.read(self.basepath + "alerts.ini")
    		database = config.get("SENSORDB", "dbname")
    		dbtype = config.get("SENSORDB", "dbtype")
	
	    	if dbtype == 'sqlite':
			self.connectSQLite(database)
		elif dbtype == 'oracle':
	      		self.connectOracle(database)
			print "Connected to Oracle Alerts"    
		else:
			raise 'DB hell'

	def __del__(self):
		self.cur.close()
		self.con.commit()
		self.con.close() 

	def Fill_SQL_METRIC (self,query,name,values):
		query = str(query)
		name = str(name)
		values = str(values)
		self.cur.execute ("""select sql_metric_sq.nextval from dual""")
		self.id = self.cur.fetchone()
        	id = self.id[0]
		sql_metric_sql = """insert into sql_metric (ID,QUERY,NAME,UNITS) values (:i,:qr,:na,:vl)"""
    		self.cur.execute(sql_metric_sql,{"i":id,"qr":query,"na":name,"vl":values})
		return id
		
	def Fill_METRIC_TYPE (self,metric_table,name):
                sql_metric_type = """insert into metric_type (METRIC_TABLE,NAME) values (:m_table,:na)"""
                self.cur.execute(sql_metric_type,{"m_table":metric_table,"na":name}) 
		return
	
        def Fill_ALERT (self,metric_id,metric_type,user_id,site_regexp):
		self.cur.execute ("""select alert_sq.nextval from dual""")
                self.id = self.cur.fetchone()
                id = str(self.id[0])
                sql_alert = """insert into sql_metric (ID,METRIC_ID,METRIC_TYPE,USER_ID,SITE_REGEXP) values (:i,:m_id,:m_type,:u_id,:s_regexp)"""
                self.cur.execute(sql_alert,{"i":id,"m_id":metric_id,"m_type":metric_type,"u_id":user_id,"s_regexp":site_regexp}) 
		return
