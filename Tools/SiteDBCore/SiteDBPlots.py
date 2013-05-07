from Framework.PluginManager import DeclarePlugin
from Framework import Controller, StaticController, templatepage, expose
from graphtool.graphs.common_graphs import PieGraph
import cStringIO

class ResourceDivision:
  """
  Plot of division of resources over tiers
  """
  plot = ''
  def __init__(self):
    self.plot = PieGraph()

  def getData(self):
    select = ""
  
  @expose  
  def showPlot(self):
    file = cStringIO.StringIO()
    metadata = {'title':'Division of resources by tier'}
    plot.run( self.getData(), file, metadata )
    return file.get_value()
    
class ResourceHistory:
  """
  Plot of all resource pledges for a site over time
  """
  plot = ''
  def __init__(self):
    self.plot = StackedBarGraph()