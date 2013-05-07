#!/usr/bin/env python
from optparse import OptionParser
from Framework.Logger import Logger
from Framework.Context import Context
from Tools.SecurityModuleCore.SecurityDBApi import SecurityDBApi
import codecs

if __name__ == "__main__":
    parser = OptionParser ()
    parser.add_option ("-f", "--file",
                       help="input HN shadow passwd",
                       default="passwd",
                       dest="source")
    parser.add_option ("-d", "--db",
                       help="target SiteDB database",
                       default="sitedb_test.db",
                       dest="db")
    options, args = parser.parse_args ()
    context = Context ()
    context.addService (Logger ("importHNShadow"))
    api = SecurityDBApi (context)
    context.Logger().message ("HN file is " + options.source )
    shadowFile = codecs.open (options.source, "r", "ascii", "replace")
    for line in shadowFile:
      contact = line.split(":")
      if " " in contact[4]:
        forename, surname =  contact[4].split (" ", 1)
      else:
        forename, surname = (contact[4], contact[4])
      api.importHNAccount (username=contact[0].encode ("ascii", "replace"), 
                           passwd=contact[1], 
                           forename=forename.encode ("ascii", "replace"),
                           email=contact[7].strip(),
                           surname=surname.encode ("ascii", "replace"))