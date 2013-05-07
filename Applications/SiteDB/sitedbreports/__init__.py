"SiteDB Reports"
"This script will generate a set of managerial reports, from queries on SiteDB"

from Tools.Reports import Report, ReportTemplate #Templates
from Tools.Reports import ImageAndFlowables, Paragraph, Spacer, Image, KeepTogether, ParagraphStyle # Layout
from Tools.Reports import A4, inch # sizes


from graphtool.tools.common import expand_string

from pylab import *
from matplotlib.text import *

class SiteResourceReport(Report):
    def __init__(self, site=None, date=None, path=None):
        Report.__init__(self, date, path)
        self.site = site

        self.pdf = ReportTemplate("%s_resource_report.pdf" % self.site.replace(" ", ""), pagesize = A4)
        
    # Methods for masthead and footer
    def myFirstPage(self, canvas, doc):
        Image('PhEDEx-banner.png', width=A4[0], height=100).drawOn(canvas, 0, (A4[1]-100))
        self.allPages(canvas, doc)

        style = self.getStyle() 
        date = self.getDate()
        P = Paragraph("SiteDB Resources Report", style["ReportTitle"])
        size = P.wrap(A4[0], 200)
        #Because we're drawing 'raw' paragraphs need to wrap them
        P.wrapOn(canvas, A4[0], size[1])
        top = 10 + size[1]
        P.drawOn(canvas, 0, A4[1]-top)
        
        P = Paragraph("Week beginning %s" % date, style["ReportTitleDate"])
        size = P.wrap(A4[0], 200)
        P.wrapOn(canvas, A4[0], size[1])
        top = top + size[1]
        P.drawOn(canvas, 0, A4[1]-top)
    
    def myLaterPages(self, canvas, doc):
        Image('PhEDEx-banner.png', width=A4[0], height=75).drawOn(canvas, 0, (A4[1]-75))
        self.allPages(canvas, doc)

        style = self.getStyle() 
        date = self.getDate()
        P = Paragraph("SiteDB Resources Report for %s" % self.site, style["ReportTitle"])
        size = P.wrap(A4[0], 200)
        P.wrapOn(canvas, A4[0], size[1])
        top = 10 + size[1]
        P.drawOn(canvas, 0, A4[1]-top)
        
    def allPages(self, canvas, doc):
        #Background images
        Image('phedex_outline.png', width=A4[0]-50, height=A4[0]-50).drawOn(canvas, 25, (A4[1]/2) - (A4[0]/2))
        
        #Footer text
        style = self.getStyle() 
        date = self.getDate()
        P = Paragraph("SiteDB Global Resource Report for quarter %s  - Page %d" % (date, doc.page), style["Footer"])
        size = P.wrap(A4[0], 200)
        P.wrapOn(canvas, A4[0]-20, size[1])
        top = 10 + size[1]
        P.drawOn(canvas, 0, top)
                
    def makeReport(self):
        style = self.getStyle()
        story = []
        
        story.append(self.doExport())
        
        story.append(self.doImport())
        
        story.append(self.doSubscriptions())
    
        story.append(PageBreak())

        story.append(self.doOutstanding())
        
        story.append(self.doErrors())
        
        self.pdf.build(story, onFirstPage=self.myFirstPage, onLaterPages=self.myLaterPages)
        
class GlobalResourceReport(Report):
    def __init__(self, date=None, path=None):
        Report.__init__(self, date, path)
        self.pdf = ReportTemplate("global_resource_report.pdf", pagesize = A4)
        
    def getStyle(self):
        style = Report.getStyle(self)
        
        style['ReportTitle'].textColor='#960000'
        style['ReportTitleDate'].textColor='#BEBEBE'
        style['ReportSubTitle'].textColor='#505050'
        style["Footer"].textColor='#BEBEBE'
        return style
                         
    def doSiteText(self):
        print "doSiteText"
        style = self.getStyle()
        # return a Paragraph object
        text = '''CMS has %s Tier One sites, %s Tier Two sites and %s Tier Three sites.''' % (1, 2, 3)
        para = Paragraph(text, style=style["Normal_just_rind"])

        return KeepTogether([para, Spacer(inch * .125, inch * .125)])
    
    def doQuarterResources(self): 
        print "doQuarterResources"
        style = self.getStyle()   
        quarter = self.getQuarter()
        text = """The following resources are currently available to CMS for 
        %s Q.%s. The plot shows what has been pledged by tier and what has 
        been delivered by tier""" % (quarter[1], quarter[0])
        
        para = Paragraph(text,style=style["Normal_just_rind"])
        
        return KeepTogether([para, Spacer(inch * .125, inch * .125)])
    
    def doResourceProjection(self):
        print "doResourceProjection"
        style = self.getStyle()
        text = """This will be a resource projection. Will have the pledged resources 
                for CMS with the delivered resources superimposed."""
        para = Paragraph(text,style=style["Normal_just_rind"])
        from reportlab.graphics.charts.linecharts import HorizontalLineChart 

        return KeepTogether([para, Spacer(inch * .125, inch * .125)])
    
    # Methods for masthead and footer
    def myFirstPage(self, canvas, doc):
        self.allPages(canvas, doc)

        style = self.getStyle() 
        date = self.getDate()
        quarter = self.getQuarter()
        P = Paragraph("SiteDB Global Resource Report", style["ReportTitle"])
        size = P.wrap(A4[0], 200)
        #Because we're drawing 'raw' paragraphs need to wrap them
        P.wrapOn(canvas, A4[0], size[1])
        top = 10 + size[1]
        P.drawOn(canvas, 0, A4[1]-top)
        
        P = Paragraph("%s Quarter %s" % (quarter[1], quarter[0]), style["ReportSubTitle"])
        size = P.wrap(A4[0], 200)
        P.wrapOn(canvas, A4[0], size[1])
        top = top + size[1]
        P.drawOn(canvas, 0, A4[1]-top)
        
        P = Paragraph("Report generated %s " % (self.getDate()), style["ReportTitleDate"])
        size = P.wrap(A4[0], 200)
        P.wrapOn(canvas, A4[0], size[1])
        top = top + size[1]
        P.drawOn(canvas, 0, A4[1]-top)
        print "Report title done"
        
    def myLaterPages(self, canvas, doc):
        self.allPages(canvas, doc)

        style = self.getStyle() 
        date = self.getDate()
        P = Paragraph("SiteDB Global Resource Report", style["ReportTitle"])
        size = P.wrap(A4[0], 200)
        P.wrapOn(canvas, A4[0], size[1])
        top = 10 + size[1]
        P.drawOn(canvas, 0, A4[1]-top)
        print "Page title done"
        
    def allPages(self, canvas, doc):
        #Footer text
        style = self.getStyle() 
        quarter = self.getQuarter()
        P = Paragraph("""SiteDB Global Resource Report for %s Q.%s
        - Page %d""" % (quarter[1], quarter[0], doc.page), style["Footer"])
        size = P.wrap(A4[0], 200)
        P.wrapOn(canvas, A4[0]-20, size[1])
        top = 10 + size[1]

        P.drawOn(canvas, 0, top)
        print "footer drawn"
               
    def makeReport(self):
        style = self.getStyle()
        story = []
        
        story.append(self.doSiteText())
        
        story.append(self.doQuarterResources())
        
        story.append(self.doResourceProjection())

        self.pdf.build(story, onFirstPage=self.myFirstPage, onLaterPages=self.myLaterPages)  
        
class ReportPlots:
    def projection(self, quarter, site=None, type='cpu', range=1):
        pass
    
    def resources(self, quarter, site=None, type='cpu'):
        #create plot of pledge vs delivered for quarter per week
        pass
    
    def breakdownbytier(self, quarter, type='cpu'):
        #Create a pie chart of resource type per tier
        pass
    
        