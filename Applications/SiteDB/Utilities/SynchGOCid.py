from optparse import OptionParser
from sqlalchemy import *

def doOptions():
    parser = OptionParser()
    usage = "This script reads a text file containing a list of CMS names, SAM names and GOCID's and updates SiteDB accordingly.\n Usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-f", "--file", dest="file",
                  help="Read list of sites/GOCID's from FILE", metavar="FILE")
    parser.add_option("-d", "--dbname", dest="dbname", metavar="DATABASEFILE",
                  help="Database connection string")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")
    
    return parser.parse_args()

if __name__ == '__main__':
    opts, args = doOptions()
    f=open(opts.file, 'r')
    if opts.dbname == None:
        print "No database given, exiting"
    else:
        con = create_engine(opts.dbname, convert_unicode=True, encoding='utf-8', pool_size=1, pool_recycle=30)
        for l in f.readlines():
            tmp = l.split()[1:]
            if len(tmp) == 2:
                sql = "update sam_name set GOCDBID=:id where name=:name"
                binds = {'id':tmp[1], 'name':tmp[0]}
                if opts.verbose:
                    print sql, binds
                con.execute(sql, binds)