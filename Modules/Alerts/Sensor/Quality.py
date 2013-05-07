#!/usr/bin/env python
import sys
import os, time, pdb
import Sensor

class Quality (Sensor.Connection):
    def __init__(self,ts):
        self.sensor = Sensor.Connection()
        self.time_span = ts*3600

    def getQuality (self):
            
        table_quality = {}
        link = ()
        quality = 0
                        
        query = """select tnf.name, tnt.name, sum(hle.done_files), sum(hle.try_files) 
                        from t_history_link_events hle 
                        join t_adm_node tnf on tnf.id = hle.from_node
                        join t_adm_node tnt on tnt.id = hle.to_node
                    where hle.timebin >= (sysdate - TO_DATE('01.01.1970:00:00:00','DD.MM.YYYY:HH24:MI:SS'))*24*60*60 - :time_span
                    group by (tnf.name, tnt.name)"""
        
        self.sensor.cursor.execute (query,{"time_span":self.time_span})
        table = self.sensor.cursor.fetchall()
                        
        for row in table:
            link = row[0], row[1]
            if (row[3]):
                quality = row[2]/row[3]
            else:
                quality = -1 
                
            table_quality [link] = quality
        
        return table_quality