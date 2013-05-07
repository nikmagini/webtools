#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "graphtool",
    version = "0.6.5",
    description = "CMS Common Graphing Package.",
    author = "Brian Bockelman",
    author_email = "bbockelm@math.unl.edu",
    package_dir = {'graphtool.static_content': 'static_content', 'graphtool': 'src/graphtool'},
    packages = find_packages('src') + ["graphtool.static_content"],
    include_package_data = True,
    zip_safe = False,

    classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: POSIX'
    ],
    
    #dependency_links = ['http://effbot.org/downloads/Imaging-1.1.6.tar.gz#egg=PIL-1.1.6'],
    #install_requires=["CherryPy<=3.1", "matplotlib<=0.90.1", "numpy", "PIL"],
   
    entry_points={
        'console_scripts': [
            'graphtool = graphtool.utilities.graphtool_cli:main'
        ]
    },
 
    #package_data = {"graphtool_static_content":["*"], "graphtool_example":["*"]}
)
