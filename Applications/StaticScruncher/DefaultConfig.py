from WMCore.Configuration import Configuration
from os import environ

config = Configuration()

# This component has all the configuration of CherryPy
config.component_('Webtools')
# We could change port, set logging etc here like so:
config.Webtools.port = 8020
#config.Webtools.environment = development
# etc. Check Root.py for all configurables

# This is the application
config.Webtools.application = 'StaticScruncher'

# This is the config for the application
config.component_('StaticScruncher')
# Define the default location for templates for the app
config.StaticScruncher.templates = None
config.StaticScruncher.admin = 'your@email.com'
config.StaticScruncher.title = 'CMS StaticScruncher'
config.StaticScruncher.description = 'The StaticScruncher concatenates, ' + \
            'minifies, caches, gzip compresses and sets appropriate expires' + \
            ' headers for static content such as css and js files. The idea' + \
            ' is to minimise the number of calls to the server and minimise' + \
            ' the data sent to the client by removing white space etc.'

# Define the class that is the application index
config.StaticScruncher.index = 'scruncher'

# Views are all pages 
config.StaticScruncher.section_('views')
# These are all the active pages that Root.py should instantiate 
active = config.StaticScruncher.views.section_('active')

# Controllers are standard way to return minified gzipped css and js
# Please install YUI or provide another reset.css file
active.section_('scruncher')
# The class to load for this view/page
active.scruncher.object = 'StaticScruncher.Scruncher'

# The scruncher maintains a library. Keys should be name-version and point to a 
# directory where this code base can be found, plus a type (currently only 
# support yui as a type)
library = active.scruncher.section_('library')
yui280 = library.section_('yui-2.8.0')
yui280.type = 'yui'
yui280.root = '/Users/metson/Downloads/yui/build'