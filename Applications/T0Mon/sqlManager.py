from sqlalchemy import *

import time
import datetime
import sys
import re

import config
import globals

connection = None

### Module for managing DB connection ###

#****************************************************************************************************
#* TO DO:zvi080926:Implementing connection pooling instead of single connection would be a good job *
#****************************************************************************************************

def print_clause(clause):
    t = str(clause)
    params = clause.compile().params
    def token(m):
        return repr(params[m.group(1)])
    return re.compile(r':(\w+)').sub(token, t)

def initBasicConnection():
    """
    Connect to DB

    Connect to DB using sqlalchemy using cx_oracle
    """
    global connection
    if (connection == None):
        engine = create_engine('oracle://' + config.DB_USER + ":" + \
            config.DB_PASSWORD + "@" + config.DB_TNS)

        globals.dbMeta = MetaData()
        globals.dbMeta.bind = engine

        connection = engine.connect()

def executeQuery(query, bindParams = None):
    """
    Execute query. Query can be sqlalchemy object or simple string.
    """
    if (connection == None):
        initBasicConnection()
    start = datetime.datetime.now()
    try:
        if 0:
            print "Executing"
            if (bindParams != None):
                print "%s" % bindParams
            if type( query ) == type( 'str' ):
                print query
            else:
                print print_clause( query )
            sys.stdout.flush()
        if (bindParams != None):
            queryResult = connection.execute(query, bindParams)
        else:
            queryResult = connection.execute(query)
    except StandardError, ex:
        # connection.close()
        raise RuntimeError, "Failed to query : %s\n" % str(ex)
    delta = datetime.datetime.now() - start
    queryResult.time = delta.seconds * 1000 + delta.microseconds / float(1000)
    if 0:
        print queryResult.time
    # connection.close()
    return queryResult
