#!/usr/bin/env python
"""
_CreateMonitor_
                                                                                
Command line tool to insert in the Alert DB the parameters necessary to
monitor a site.

"""

import sys, os, string, getopt, time, pdb
import ConfigParser
from optparse import OptionParser
pdb.set_trace()

class SetupAlert:

    conn = ''
    cursor = ''
    basepath = ''

    user_id = 0 
    sensor_attr = []
    sensor_param = {}
    alarm = {}
    alert = ''

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

        self.cursor.close()
        self.conn.commit()
        self.conn.close()
        print "Disconnected from ALERT"


    def connectOracle(self, database):

        import cx_Oracle
        cx_Oracle.threaded=True
        self.conn = cx_Oracle.connect(database)
        self.cursor = cx_Oracle.Cursor(self.conn)	
        print "Connected to ALERT"
        
    def getUserId(self):
        return self.user_id

    def getSensorAttr(self):
        return self.sensor_attr

    def getSensorParam(self,key):
        return self.sensor_param[key]

    def getAlarm(self,key):
        return self.alarm[key]

    def getAlert(self):
        return self.alert

    def setUserId(self,arg):
        self.user_id = arg
        print "User Id: "+arg	
        return

    def setSensorAttr(self,arg):
        self.sensor_attr = arg
        print "Sensor Attributes: "
        for k in self.sensor_attr:
            print k
        return


    def setSensorParam(self,arg):
        self.sensor_param = arg
        for k,v in self.sensor_param.iteritems():
            print "Sensor: "+k
            print v
        return
            
    def setAlarm(self,arg):
        self.alarm = arg
        for k,v in self.alarm.iteritems():
            print "Alarm: "+k
            print v
        return
            
    def setAlert(self,arg):
        self.alert = arg
        print "Alert Attributes: "
        for k in self.alert:
            print k
        return	
        
    def insertOperator (self,operator):
    
        check_query = """select operator_id from operator where value=:value"""
        insert_query = """insert into operator (operator_id,value) values (operator_sq.nextval,:value)"""
        
        self.cursor.execute(check_query,{"value":operator})
        operator_exists = self.cursor.fetchone()
        if operator_exists == None:
            self.cursor.execute(insert_query,{"value":operator})
        if operator_exists == None:
            self.cursor.execute("""select operator_sq.currval from dual""")
            tmp = self.cursor.fetchone()
            operator_id = tmp[0]
        else:
            operator_id = operator_exists[0]
        
        return operator_id

    def insertAlarm (self,name,user_sensor):

        alarm_param = self.getAlarm(name)
        check_query = """select alarm_id from alarm where user_sensor_id=:user_sensor_id 
                         and threshold=:threshold and   operator_id=:operator_id"""
        insert_query = """insert into alarm (alarm_id,user_sensor_id,threshold,operator_id) values
                          (alarm_sq.nextval,:user_sensor_id,:threshold,:operator_id)"""

        op = self.insertOperator(alarm_param[0])
        ts = alarm_param[1]
        self.cursor.execute(check_query,{"user_sensor_id":user_sensor,"threshold":ts,"operator_id":op})
        alarm_exists = self.cursor.fetchone()

        if alarm_exists == None:
            self.cursor.execute(insert_query,{"user_sensor_id":user_sensor,"threshold":ts,"operator_id":op})
        return
            
            
    def insertUserSensor (self,name,sensor,scpt,desc):

        param = self.getSensorParam(name)
        user = self.getUserId()
                
        check_query = """select user_sensor_id from user_sensor where sensor_id=:sensor_id 
                         and user_id=:user_id and parameters=:parameters and script=:script"""
        insert_query = """insert into user_sensor (user_sensor_id,sensor_id,user_id,parameters,script,description) 
                          values (user_sensor_sq.nextval,:sensor_id,:user_id,:parameters,:script,:description)"""

        self.cursor.execute(check_query,{"sensor_id":sensor,"user_id":user,"parameters":param,"script":scpt})
        user_sensor_exists = self.cursor.fetchone()                        
        
        if user_sensor_exists == None:
            self.cursor.execute(insert_query,{"sensor_id":sensor,"user_id":user,"parameters":param,"script":scpt,"description":desc})
        
        if user_sensor_exists == None:
            self.cursor.execute("""select user_sensor_sq.currval from dual""")
            tmp = self.cursor.fetchone()
            user_sensor_id = str(tmp[0])
        else:
            user_sensor_id = str(user_sensor_exists[0])
        
        self.insertAlarm(name,user_sensor_id)
        
        return
                                    
    def insertSensor (self):
    
        sen_attr = self.getSensorAttr()                 	#sen = [n1,p1,d1],[n2,p2,d2]
        check_query = """select sensor_id from sensor where name=:name"""
        insert_query = """insert into sensor (sensor_id,name) values (sensor_sq.nextval,:name)"""


        
        for attr in sen_attr:
            sensor_name = attr[0]
            sensor_script = attr[1]
            sensor_description = attr[2]
    
            self.cursor.execute(check_query,{"name":sensor_name})
            sensor_exists = self.cursor.fetchone()

            if sensor_exists == None:
                self.cursor.execute(insert_query,{"name":sensor_name})         

            if sensor_exists == None:
                self.cursor.execute("""select sensor_sq.currval from dual""")
                tmp = self.cursor.fetchone()
                sensor_id = str(tmp[0])
            else:
                sensor_id = str(sensor_exists[0])
            
            self.insertUserSensor(sensor_name,sensor_id,sensor_script,sensor_description)

        self.insertAlert()
                
        def insertAlert (self):

            user = self.getUserId()
            al_attr = self.getAlert()
            
            comb = al_attr[0]
            act = al_attr[1]

            check_query = """select alert_id from alert where user_id=:user_id and combination=:combination"""
            insert_query = """insert into alert (alert_id,user_id,combination,actuator) values (alert_sq.nextval,:user_id,:combination,:actuator)"""

            
            self.cursor.execute(check_query,{"user_id":user,"combination":comb})
            if self.cursor.fetchone()==None:
                self.cursor.execute(insert_query,{"user_id":user,"combination":comb,"actuator":act})                              
            return


if __name__ == '__main__':

    valid = ['UserId=','SensorAttr=','SensorParameters=','AlarmParameters=','AlertAttr=']	
    
    try:
            opts, args = getopt.getopt(sys.argv[1:], "", valid)
            
    except getopt.GetoptError, ex:
            self.usage()
            sys.exit(2)
    
    try:

        alert = SetupAlert()

        for opt, arg in opts:
            if opt == "--UserId":                       #187 <- given by SiteDB
                alert.setUserId(arg)
            if opt == "--SensorAttr":   
                aux = []
                sensor_attr = []
                tmp1 = arg.split(';')                   #tmp1 = [n1,p1,d1], [n2,p2,d2]  list
                        
                for tmp2 in tmp1:
                    aux = tmp2.split(',')               #aux = [n1 , p1 , d1] list

                    aux[0]=aux[0].replace('[','')
                    aux[2]=aux[2].replace(']','')
    
                    sensor_attr.append(aux)

                alert.setSensorAttr(sensor_attr)
                    
            if opt == "--SensorParameters":	
                sensor_param = {}
                tmp1 = arg.split(';')
                
                for tmp2 in tmp1:
                    tmp3 = tmp2.split(':')

                    sensor_param [tmp3[0]] = tmp3[1]	
                
                alert.setSensorParam(sensor_param)
                    
            if opt == "--AlarmParameters":                      #RATE:[<,10];QUALITY:[<=,90]
                aux = {}
                alarm = {}
                alarm_args = []
                tmp1 = arg.split(';')
                for tmp2 in tmp1:
                    tmp3 = tmp2.split(':')
                    aux [tmp3[0]] = tmp3[1]
                for k,v in aux.iteritems():
                    tmp1 = v.split(',')
                    alarm_args = []
                    tmp1[0]=tmp1[0].replace('[','')
                    alarm_args.append(tmp1[0])
                    tmp1[1]=tmp1[1].replace(']','')
                    alarm_args.append(tmp1[1])
                    alarm [k] = alarm_args
        
                alert.setAlarm(alarm)
                    
            if opt == "--AlertAttr":
                alert_attr = []
                alert_attr = arg.split(':')                     #tmp1 = [A1&&A2||A3]:/path
                
                alert_attr[0]=alert_attr[0].replace('[','')
                alert_attr[0]=alert_attr[0].replace(']','')
        
                alert.setAlert(alert_attr)
                
        alert.insertSensor()
    
    except:
        import traceback
        traceback.print_exc(file = file('trace.txt', 'w'))
        print "HELL"	
                                    
    def usage():
        usg="""Usage: CreateMonitor.py <options> \n Options: \n
        --UserId=<user_id> \n
        Given by SiteDB
                        e.g. 123
        Dictionary containing contact method and value. \n\t\t
        
        --SensorAttr=<'[p11,p12,p13];[p21,p22,p23]'>
        List containing the sensor name, the script name and a comment about the sensor.
                        e.g. 'RATE,/home/phedex/sensor, blah bla bla';'QUALITY,/home, bleh bleh bleh' \n
                        
        --SensorParameters=<'key1:{key11=value11,key12=value12};key2:{key21=value21,key22=value22}'> \n
        Dictionary containing keys as Sensor Name and values as dictionary of parameters for that sensor. \n \t\t
                        e.g. 'RATE:{to_node=T1_CERN_Buffer,from_node=T1_FNAL_Buffer,time_span=1};
                            QUALITY:{to_node=T1_CERN_Buffer,from_node=T1_FNAL_Buffer,time_span=10}' \n
        
        --AlarmParameters=<'key1:[p11,p12];key2:[p21,p22]'> \n
        Dictionary containing keys as Sensor Name and values as a list of parameters for the alarm related to that
        sensor. The first parameter for a sensor is the operator and the second is the threshold. \n\t\t
        e.g. 'RATE:[<,10];QUALITY:[<=,90]' \n
        
        --AlertAttr=<key:value> \n
        String describing the combination of sensors that should trigger an alert to the user and
        the actuator defined to that situation. The alarms is related to  \n\t\t
                        e.g. '[USID1||USID2&&USID3]:/home/phedex/FileDowload -restart'\n"""
        print usg
        return

    

