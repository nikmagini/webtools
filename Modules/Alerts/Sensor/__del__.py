#!/usr/bin/env python
import sys
import os, time, pdb

class Sensor:

	def __del__(self):
		self.cursor.close()
		self.conn.commit()
		self.conn.close()      
		print "Disconnected from TMDB"
