#!/usr/bin/env python
from distutils.core import setup, Command
import os, sys
"""
Build and set up the environment for StaticScruncher
"""
def get_relative_path():
    return os.path.dirname(os.path.abspath(os.path.join(os.getcwd(), sys.argv[0])))

class EnvCommand(Command):
    description = "Configure the PYTHONPATH, DATABASE and PATH variables to" +\
    "some sensible defaults, if not already set. Call with -q when eval-ing," +\
    """ e.g.:
        eval `python setup.py -q env`
    """
    
    user_options = [ ]
    
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass
    
    def run(self):
        here = get_relative_path().strip('/').split('/')
        here = '/' + '/'.join(here[:-1])
        pypath = os.getenv('PYTHONPATH', '').strip(':').split(':')
        
        if here not in pypath:
            pypath.append(here)
              
        print 'export PYTHONPATH=%s' % ':'.join(pypath)

def getPackages(package_dirs = []):
    packages = []
    for dir in package_dirs:
        for dirpath, dirnames, filenames in os.walk('./%s' % dir):
            # Exclude things here
            if dirpath not in ['./src/python/', './src/python/IMProv']: 
                pathelements = dirpath.split('/')
                if not 'CVS' in pathelements:
                    path = pathelements[3:]
                    packages.append('.'.join(path))
    return packages

package_dir = {'StaticScruncher': '.'}

setup (name = 'wmcore',
       version = '1.0',
       maintainer_email = 'hn-cms-wmDevelopment@cern.ch',
       cmdclass = {'env': EnvCommand},
       package_dir = package_dir,
       packages = getPackages(package_dir.values()),)

