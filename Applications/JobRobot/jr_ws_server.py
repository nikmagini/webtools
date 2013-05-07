#!/usr/bin/env python

"""
JobRobot static file service.
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
        page = ''.join(open(self.path+'/index.html','r').readlines() )
        return page
    index.exposed=True

if __name__ == '__main__':
    # load location of the path from jr.conf
    # this path defines location of files which will be served
    # by this data-services. Those files are uploaded to the server
    # by operator. The path is defined in /data/projects/conf/jobrobots
    # area
    for line in open(os.path.join(os.path.split(__file__)[0], 'jr.conf'),'r')\
                .readlines():
        if  line and line.lower()[0] == "#": 
            continue # it's comment
        if  line.lower().find('path')!=-1:
            path = line.replace('PATH=', '').replace('path=', '')\
                   .replace('\n', '')
    print "+++ Reading", path
    cherrypy.config.update({'server.socket_port': 8101,
                            'server.thread_pool': 20,
                            'environment': 'production',
                            'log.screen':True,
                            'log.error_file':"jr.log",
                           })

    conf={'/': {'tools.staticdir.root': os.path.split(__file__)[0],
                'tools.response_headers.on':True,
                'tools.response_headers.headers':
                 [('Expires','Thu, 15 Apr 2010 20:00:00 GMT'),
                  ('Cache-Control','no-store, no-cache, must-revalidate,post-check=0, pre-check=0')],
                'tools.staticdir.on': True,
                'tools.staticdir.dir':path
                       },
          '/html':{'tools.staticdir.on':True,
                   'tools.staticdir.dir':path
                  },

        }
    cherrypy.quickstart(Main(path), '/', config=conf)
