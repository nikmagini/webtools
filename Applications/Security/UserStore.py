"""
A UserStore gives the security module a way to determine a users sReg 
information and to check their username and password.
"""
import cherrypy
import logging

class UserStore:
	def __init__(self, config):
		self.store = config.source
		
	def get(self, user):
		"""
		pull in the user or return a null user, a standard wrapper around 
		self.load - call this but don't subclass it!!
		"""
		try:
			return self.load(user)
		except Exception, e:
			cherrypy.log(e, context='UserStore', 
						 severity=logging.INFO, traceback=False)
			
			return {'permissions'  : None,
			    'fullname'  : None,
			    'dn': None}
	
	def load(self, user):
		"""
		load the user information from the store, return a dict representing 
		the user
		"""
		assert 1 == 2
	
	def checkpass(self, user, password):
		"""
		Check the password is what the store holds for the user. Return 
		true/false
		"""
		return False
	
	def checkdn(self, user, dn):
		"""
		Check that the user and dn match up, return true/false
		"""
		return False

	def getuserbydn(self, dn):
		"""
		get the username for a given dn. return the user name or None
		"""
		return None
