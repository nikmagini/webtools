class CmdLineArgs (object):
    def __init__ (self, optionParser):
        self.opts, self.args = optionParser.parse_args ()
    