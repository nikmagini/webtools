"Backup a SiteDB database to an SQLite file, and restore that database from the file"

#!/usr/bin/env python
from optparse import OptionParser
from sqlalchemy import *

def Options():
    parser = OptionParser ()
    parser.add_option ("-i", "--in",
                       help="Read input from DATABASE",
                       metavar = "DATABASE",
                       dest="input")
    parser.add_option ("-o", "--out",
                       help="Write output to DATABASE, which already has the SiteDB schema loaded",
                       metavar = "DATABASE",
                       dest="output")
    parser.add_option ("-c", "--create",
                       help="Create a new sqlite file at DATABASE, and write output to it",
                       metavar = "DATABASE",
                       dest="create")
    parser.add_option ("--check",
                       help="Check the number of entries in each table",
                       action="store_true",
                       dest="check")
    parser.add_option ("-d", "--dummy",
                       help="""Run the select's but don't create the new database 
                       file, print the result of the selects""",
                       action="store_true",
                       dest="dummy")
    parser.add_option ("-v", "--verbose",
                       help = "Print each select, insert and the data",
                       action="store_true", 
                       dest = "verbose")
    
    options, args = parser.parse_args ()
    return options.input, options.output, options.create, options.dummy, options.verbose, options.check

if __name__ == "__main__":
    
    indb, outdb, create, dummy, verbose, check = Options()

    if indb:
        indb = create_engine(indb).connect()
    else:
        raise "No input database provided. Exiting"
        
    outdb = None
    if outdb:
        outdb = create_engine(outdb).connect() 
    else:
        print "No output database provided."
        if create:
            print "Creating database: %s" % create
            outdb = create_engine(create).connect() 
        elif dummy or check:
            print "running dummy or check mode, so it's OK"
        else:
            raise "not running dummy mode, so it's bad."
            
    
    tables = [#'survey', 
              #'survey_who', 'survey_tiers', 'survey_roles', 
              'tier', 'site', 'site_association', 'resource_element', 'phedex_node',
              'resource_pledge', #'resource_delivered', 
              'performance', 'job_activity', 
              'contact', 'user_passwd', 'crypt_key', 
              'role', 'user_group', 'site_responsibility', 'group_responsibility', 
              #'question', 'question_default', 'question_answer'
              ]

    meta = MetaData()

    for t in tables:
        if check:
            print t, indb.execute('select count(*) from %s' % t).fetchall()
        else:
            print t

        select = 'select * from %s' % t
        if verbose:
            print select
#        try:   
        #data = indb.execute(select)
        table = Table(t, meta, autoload=True, autoload_with=indb)
        data = indb.execute(table.select()).fetchall()
        if dummy or verbose:
            print table, table.columns
        if verbose:
            print data
        if create:
            #meta.create_all()
            table.create(outdb)
        for d in data:
            #INSERT INTO table_name (column1, column2,...) VALUES (value1, value2,....)
            fields = ""
            values = ""
            for c in table.columns:
                type = "%s" % c.type
                cstr = "%s" % c
                fields = "%s %s," % (fields, cstr.split('.')[1])
                if type.split('(')[0] == 'SLString' or type.split('(')[0] == 'SLChar':
                    cstr = '"%s"' % d[c]                   
                else:
                    if d[c]:
                        cstr = "%s" % d[c]
                    else:
                        cstr = 0
                values = "%s %s," % (values, cstr)
                
            insert = "INSERT INTO %s (%s) VALUES (%s)" % (table, fields.rstrip(','), values.rstrip(','))
            if verbose:
                print insert
            if not dummy:
                outdb.execute(insert)
        if not dummy and check:
            print t, outdb.execute('select count(*) from %s' % t).fetchall()
        if not dummy and verbose:
            print outdb.execute(select).fetchall()
        print            
            #outdb.commit()
#        except Exception, e:
#            print e
    #Close up
    if outdb:
        outdb.close()
    if indb:
        indb.close()
            
            
            
            
            