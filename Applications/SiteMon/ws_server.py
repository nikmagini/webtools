#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
# Author:  Valentin Kuznetsov, 2008

"""
Simple server to serve site monitoring tools, jobrobot, ssb, sam
"""

import os
import cherrypy

class Main(object):
    def __init__(self,path):
        self.path = path

    def index(self):
        page  = 'Welcom to site monitoring page'
        page += '<ul>'
        page += '<li><a href="/jobrobot/">JobRobot</a></li>'
        page += '<li><a href="/sam/">SAM</a></li>'
        page += '<li><a href="/ssb/">SSB</a></li>'
        page += '</ul>'
        return page
    index.exposed=True

    def jobrobot(self):
        page = ''.join(open(self.path+'/jobrobot/index.html','r').readlines())
        return page
    jobrobot.exposed=True

    def sam(self):
        page = ''.join(open(self.path+'/sam/index.html','r').readlines())
        return page
    jobrobot.exposed=True

    def ssb(self):
        page = ''.join(open(self.path+'/ssb/index.html','r').readlines())
        return page
    jobrobot.exposed=True

if __name__ == '__main__':
    file = os.path.split(__file__)[0]
    path = os.path.join(os.getcwd(),'html')
    for line in open(os.path.join(file, 'ws.conf'), 'r').readlines():
        if  line and line.lower()[0] == '#':
            continue # it's comment
        if  line.lower().find('path') != -1:
            path = line.replace('PATH=', '').replace('path=', '').replace('\n', '')
    print "+++ Reading",path
    cherrypy.config.update({'server.socket_port': 8101,
                            'server.thread_pool': 20,
                            'environment': 'production',
                            'log.screen':True,
                            'log.error_file':"ws.log",
                           })

    conf={'/': {'tools.staticdir.root': os.path.split(__file__)[0],
                'tools.response_headers.on':True,
                'tools.response_headers.headers':
                  [('Expires', 'Thu, 15 Apr 2010 20:00:00 GMT'),
                   ('Cache-Control',
                    'no-store,no-cache,must-revalidate,post-check=0,pre-check=0')],
                'tools.staticdir.on': True,
                'tools.staticdir.dir':path
                        },
          '/html':{'tools.staticdir.on':True,
                    'tools.staticdir.dir':path
                   },

         }
    cherrypy.quickstart(Main(path), '/', config=conf)
