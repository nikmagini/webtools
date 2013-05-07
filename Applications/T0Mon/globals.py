### Module for global variables ###
### It is a bad idea to have global variables, but you can not avoid it sometimes ###
### There are comments which modules are allowed to read and to write each variables ###

# Web page GET and POST parameters
# [Write]
#   __init__ (and historyPages) on page load
# [Read]
#   utils

pageParams = None

# DB meta information
# [Write]
#   sqlManager
# [Read]
#   utils

dbMeta = None

# Logger
# [Write]
#   __init__ on startup
# [Read]
#   everybody

logger = None

# makeStatic
# [Write]
#   __init__::index on first call
# [Read]
#   __init__::index later

makeStatic = None

# debug flag
# print useful information about queries executed
# [Write]
#   never
#  [Read]
#  guiProvider::readQuery()
#  historyPages()  [it prints the dependancy table]
debugPrintQueries = False
