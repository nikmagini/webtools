#!/usr/bin/env python

"""
Crab static files service
"""
import cherrypy, os, string

class Main(object):
    """Main class used by CherryPy server to serve jobrobot services"""
    def __init__(self,path):
        """Constructor"""
        self.path=path

    def index(self):
        """
        Define content of main page.
        """
        page = "CRAB config file home page"
        page+= "<ul>"
        dir = os.path.join(os.path.split(__file__)[0],'files')
        dir = self.path
        for f in os.listdir(dir):
            page+="""<li><a href="files/%s">%s</a></li>"""%(f,f)
        page+= "</ul>"
        return page
    index.exposed=True

if __name__ == '__main__':
    # load location of the path from crab.conf
    # this path defines location of files which will be served
    # by this data-services. Those files are uploaded to the server
    # by operator. The path is defined in /data/projects/conf/crab
    # area
    for line in open(os.path.join(os.path.split(__file__)[0], 'crab.conf'),'r')\
                .readlines():
        if  line and line.lower()[0]=="#":
            continue # it's comment
        if  line.lower().find('path')!=-1:
            path=line.replace('PATH=','').replace('path=','').replace('\n','')
    print "+++ Reading", path
    cherrypy.config.update({'server.socket_port': 8102,
                            'server.thread_pool': 20,
                            'environment': 'production',
                            'log.screen':True,
                            'log.error_file':"crab.log",
                          })
    conf={'/': {'tools.staticdir.root': os.getcwd(),
                'tools.staticdir.on':True,
                'tools.staticdir.dir':path,
                'tools.staticdir.content_types':{'conf':'text/plain'},
               },
         }
    cherrypy.quickstart(Main(path), '/', config=conf)
