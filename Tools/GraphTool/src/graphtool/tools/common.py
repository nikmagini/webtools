
import math
import time
import types
import datetime
import calendar
import re

def parseOpts( args ):
  # Stupid python 2.2 on SLC3 doesn't have optparser...
  keywordOpts = {}
  passedOpts = []
  givenOpts = []
  length = len(args)
  optNum = 0
  while ( optNum < length ):
    opt = args[optNum]
    hasKeyword = False
    if len(opt) > 2 and opt[0:2] == '--':
      keyword = opt[2:] 
      hasKeyword = True
    elif opt[0] == '-':
      keyword = opt[1:]
      hasKeyword = True
    if hasKeyword: 
      if keyword.find('=') >= 0:
        keyword, value = keyword.split('=', 1)
        keywordOpts[keyword] = value
      elif optNum + 1 == length:
        passedOpts.append( keyword )
      elif args[optNum+1][0] == '-':
        passedOpts.append( keyword )
      else:
        keywordOpts[keyword] = args[optNum+1]
        optNum += 1
    else:
      givenOpts.append( args[optNum] )
    optNum += 1
  return keywordOpts, passedOpts, givenOpts

datestrings = ['%x %X', '%x', '%Y-%m-%d %H:%M:%S']

def convert_to_datetime( string ):
      results = None
      orig_string = str( string )
      if type(string) == datetime.datetime or \
         type(string) == types.FloatType or \
         type(string) == types.IntType:
        results = string
      elif type(string) == str and string.isdigit():
        results = int(string)
      else:
        t = None
        for dateformat in datestrings:
          try:
            t = time.strptime(string, dateformat)
            timestamp = calendar.timegm(t) #-time.timezone
            results = datetime.datetime.utcfromtimestamp(timestamp)
            break
          except:
            pass
        if t == None:
          try:
            string = string.split('.', 1)[0]
            t = time.strptime(string, dateformat)
            timestamp = calendar.timegm(t) #-time.timezone
            results = datetime.datetime.utcfromtimestamp(timestamp)
          except:
            raise ValueError("Unable to create time from string!")

      if type(results) == types.FloatType or type(results) == types.IntType:
        results = datetime.datetime.utcfromtimestamp( int(results) )
      elif type(results) == datetime.datetime:
        pass
      else:
        raise ValueError( "Unknown datetime type!" )

      return results

def to_timestamp( val ):
    val = convert_to_datetime( val )
    return calendar.timegm( val.timetuple() )

def expand_string( string, vars ):
  vars = dict( vars )
  for key in vars.keys():
    string = string.replace( '$' + str(key), str(vars[key]) )
  return string
 
def import_module( module_name ):
  module_list = module_name.split('.')
  module = __import__( module_name )
  if len(module_list) > 1:
    for mod_name in module_list[1:]:
      try:
        module = getattr( module, mod_name )
      except AttributeError, ae:
        #print "Module %s has no submodule named %s" % (str(module), mod_name)
        raise ae
  return module 

