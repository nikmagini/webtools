#!/usr/bin/env python
import sys
import os, time, pdb
import ConfigParser
from optparse import OptionParser
pdb.set_trace()

class Alert:

    conn = ''
    cursor = ''
    basepath = ''
    quality = {}
    rate = {}
    proxy = {}
    agent_status = {}

    def __init__(self): 
    
        self.basepath = __file__.replace(__file__.split('/')[-1], '')
        config = ConfigParser.ConfigParser()
        config.read(self.basepath + "alerts.ini")
        database = config.get("ALERT", "dbname")
        dbtype = config.get("ALERT", "dbtype")
        if dbtype == 'oracle':
            self.connectOracle(database)
        else:
            raise 'DB hell'

    def __del__(self):
    
        print "Disconnected from ALERT"

    def connectOracle(self, database):
    
        import cx_Oracle
        cx_Oracle.threaded=True
        self.conn = cx_Oracle.connect(database)
        self.cursor = cx_Oracle.Cursor(self.conn)
        print "Connected to ALERT"
            
    def AlertStatus(self):
    
        query = """select name from sensor"""
        self.cursor.execute(query)
        sensor = self.cursor.fetchall()
                        
        for row in sensor:
            self.getAllResults(str(row[0]))
                
        query = """select * from alert"""
        self.cursor.execute(query)
        alert = self.cursor.fetchall()

        metric={}
                        
        for row in alert:
            alert_id = row[0]
            user = row[1]
            combination = row[2]
            actuator = row[3]
            #atm combination is equal to 1 and just 1 alarm without any logical operation
    
            query = """select * from alarm where user_sensor_id = 
                       (select user_sensor_id from user_sensor where user_id = :user_id and
                       sensor_id = (select sensor_id from sensor where name = :name))"""

            self.cursor.execute(query,{"user_id":user,"name":combination})
            alarm = self.cursor.fetchone()
            status, current_value = self.AlarmStatus(str(alarm[0])) 

            #status = 1     ->  should trigger an alert        
            #status = 0     ->  shouldn't trigger an alert
            #status = -1    ->  no information about the ALERT in the database
                            
            if (status == 1):
                metric[combination]=current_value
                #try actuator
                #store in some table to be created how many attempts
                #if attempts > limit raise an alert
                print "User ID= "+str(user)
                print combination+"= "+str(current_value) 
                print "Alert Sent!"
                from Utilities import Mailing
                mail = Mailing.Mailing()
#                mail.sendMailUnix(user,metric)       #user_id, metric
                mail.sendMailPy(user,metric)       #user_id, metric

        print "Alarm status verified"
        return
    
    def AlarmStatus(self,alarm):
        query = """select a.threshold,o.value,u.parameters,u.script,s.name 
                    from alarm a
                        left join operator o on a.operator_id = o.operator_id
                        left join user_sensor u on a.user_sensor_id = u.user_sensor_id
                        left join sensor s on u.sensor_id = s.sensor_id
                    where alarm_id=:alarm_id"""
                    
        self.cursor.execute(query,{"alarm_id":alarm})
        alert_info = self.cursor.fetchone()
        threshold = alert_info[0]
        operator = alert_info[1]
        parameters = alert_info[2]
        script = alert_info[3]
        sensor = alert_info[4]

        current_value = self.getSensorMetric(sensor,parameters)
        if (current_value != -1):
            from Utilities import Test
            test_metric = Test.Test()
            test = test_metric.Test(current_value,operator,threshold)

            if (test):
                return 1, current_value            #alert on 40 < 50
        
            else: 
                return 0, current_value            #alert off 60 < 50

        else:
            return -1, -1                

    def getAllResults(self,sensor):
        print sensor
                
        if sensor == 'RATE':
            time_span = 1                       #in hour
            from Sensor import Rate
            rt = Rate.Rate(time_span)
            self.rate=rt.getRate()
                
        elif sensor == 'QUALITY':       
            time_span = 1                       #in hour
            from Sensor import Quality
            qual = Quality.Quality(time_span)
            self.quality=qual.getQuality()
                
        elif sensor == 'PROXY':
            from Sensor import Proxy
            prx_sts = Proxy.Proxy()
            self.proxy=prx_sts.getProxy()

        elif sensor == 'AGENTSTATUS':              
            from Sensor import AgentStatus
            agt_sts = AgentStatus.AgentStatus()
            self.agent_status=agt_sts.getAgentStatus()
        else:
            raise "Sensor HELL"

    def getSensorMetric(self,sensor,parameters):

        if sensor == 'RATE':
            link = ()
            tmp1 = parameters.split(',')
            aux = {}
            for tmp2 in tmp1:
                tmp3=tmp2.split('=')
                tmp3[0]=tmp3[0].replace('{','')
                tmp3[1]=tmp3[1].replace('}','')
                aux[tmp3[0]]=tmp3[1]
            link = aux['to_node'],aux['from_node']
            
            if (self.rate.has_key(link)):
                value=self.rate[link]
            else:
                value=-1
                
        elif sensor == 'QUALITY':
            link = ()
            tmp1 = parameters.split(',')
            aux = {}
            for tmp2 in tmp1:
                tmp3=tmp2.split('=')
                tmp3[0]=tmp3[0].replace('{','')
                tmp3[1]=tmp3[1].replace('}','')
                aux[tmp3[0]]=tmp3[1]
                    
            link = aux['to_node'], aux['from_node']
            if (self.quality.has_key(link)):
                value=self.quality[link]
            else:
                value=-1
                        
        elif sensor == 'PROXY':
            site = ''
            tmp = parameters.split('=')
            aux [tmp[0]]= tmp[1]
            site = aux['node']		
            if (self.proxy.has_key(site)):
                value=1
            else:
                value=0

        elif sensor == 'AGENTSTATUS':

            tmp1 = parameters.split(',')
            aux = {}
            for tmp2 in tmp1:
                tmp3=tmp2.split('=')
                tmp3[0]=tmp3[0].replace('{','')
                tmp3[1]=tmp3[1].replace('}','')
                aux[tmp3[0]]=tmp3[1]
            
            if (self.agent_status.has_key(site,agent)):
                value=self.agent_status[site,agent]
            else:
                value=-1
                        
        else:
            raise "Sensor HELL"

        return value	
    
                
if __name__ == '__main__':

    try:
        alert = Alert()
        alert.AlertStatus ()
            
    except:
        import traceback
        traceback.print_exc(file = file('trace.txt', 'w'))
