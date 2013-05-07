import sys
import os, pdb
import ConfigParser
from optparse import OptionParser

class Sensor:

	def __init__(self):  
    		con = ''
    		cur = ''
    		basepath = ''
    		#Move these to framework?
    		self.basepath = __file__.replace(__file__.split('/')[-1], '')
    		config = ConfigParser.ConfigParser()
    		config.read(self.basepath + "alerts.ini")
    		database = config.get("TMDB", "dbname")
    		dbtype = config.get("TMDB", "dbtype")
	
	    	if dbtype == 'sqlite':
      			self.connectSQLite(database)
    		elif dbtype == 'oracle':
	      		self.connectOracle(database)
    		else:
      			raise 'DB hell'

	def __del__(self):
		self.cur.close()
		self.con.close()      
          
	def connectOracle(self, database):
    		import cx_Oracle
    		cx_Oracle.threaded=True
    		self.con = cx_Oracle.connect(database)
    		self.cur = cx_Oracle.Cursor(self.con)
    		print "Connected to TMDB"

	def connectSQLite(self, database):
    		from pysqlite2 import dbapi2 as sqlite
    		self.con = sqlite.connect(database)    
      
	def getRate (self,to_node, from_node):
        	to_node_id = self.getNodeID (to_node)
        	from_node_id = self.getNodeID (from_node)
		
        	self.cur.execute ("""select nvl(sum(done_bytes),0)/1048576/3600 rate from t_history_link_events where timebin >= (sysdate - TO_DATE('01.01.1970:00:00:00','DD.MM.YYYY:HH24:MI:SS'))*24*60*60 - 7200 and to_node = :tnd and from_node = :fnd""",{"tnd":to_node_id,"fnd":from_node_id})
		
        	self.rate = self.cur.fetchone()
        	return str(self.rate[0])

	def getQuality (self, to_node, from_node):
        	to_node_id = self.getNodeID (to_node)
        	from_node_id = self.getNodeID (from_node)
	
		self.cur.execute ("""select (nvl(sum(done_files),0), (nvl(sum(done_files),0)+nvl(sum(fail_files),0)) from t_history_link_events where timebin >= (sysdate - TO_DATE('01.01.1970:00:00:00','DD.MM.YYYY:HH24:MI:SS'))*24*60*60 - 7200 and to_node = :tnd and from_node = :fnd""",{"tnd":to_node_id,"fnd":from_node_id})
	
        	self.quality = self.cur.fetchall()
        	if (str(self.quality[1])):
			qual = str(self.quality[0])/str(self.quality[1])
		else: 
			qual = -1
		return qual

	def getAgentStatus (self, node, agent, time_no_report):

        	node_id = self.getNodeID (node)
        	agent_id = self.getAgentID(agent)
        	self.cur.execute ("""select state from t_agent_status where node = :nd and agent = :ag""",{"nd":node_id,"ag":agent_id})
        	self.state = self.cur.fetchone()
        	return str(self.state[0])

	
	def getNodeID (self, node):
        	self.cur.execute ("""select id from t_adm_node where name = :nd""",{"nd": node})
        	self.id = self.cur.fetchone()
        	return str(self.id[0])

	def getAgentID (self, agent):
        	self.cur.execute ("""select id from t_agent where name = :ag""",{"ag":agent})
        	self.id = self.cur.fetchone()
        	return str(self.id[0])
