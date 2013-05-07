from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm, inch, pica
from reportlab.platypus import Paragraph, SimpleDocTemplate, BaseDocTemplate, Spacer, PageTemplate
from reportlab.platypus.frames import Frame
from reportlab.platypus.flowables import ImageAndFlowables, Image, KeepTogether, Preformatted
from reportlab.platypus.doctemplate import FrameBreak, PageBreak
from reportlab.platypus.tables import Table
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors 

from ReportLabExtensions import HypenatedParagraph

import os
import datetime
import time

def _doNothing(canvas, doc):
    "Dummy callback for onPage"
    pass

class ReportTemplate(SimpleDocTemplate):
    _invalidInitArgs = ('pageTemplates',)

    def __init__(self, filename, **kw):
        SimpleDocTemplate.__init__(self, filename, **kw)
    
    def build(self, flowables, onFirstPage=_doNothing, onLaterPages=_doNothing, canvasmaker=Canvas):
        #Override the build method
        self._calc()    #in case we changed margins sizes etc
        self.canvas = canvasmaker
        firstFrame = Frame(10,        # X
                       0,            # Y
                       A4[0]-20,     # width
                       A4[1]-106,     # height
                       id='normal')

        secondFrame = Frame(10,          # X
                       0,            # Y
                       A4[0]-20,     # width
                       A4[1]-46,     # height
                       #showBoundary=True,
                       id='normal')        
        
        self.addPageTemplates([PageTemplate(id='First',
                                            frames=[firstFrame],
                                            pagesize=self.pagesize,
                                            onPage=onFirstPage),
                                PageTemplate(id='Later',
                                            frames=[secondFrame],
                                            pagesize=self.pagesize,
                                            onPage=onLaterPages),
                                ]
        )
        if onFirstPage is _doNothing and hasattr(self,'onFirstPage'):
            self.pageTemplates[0].beforeDrawPage = self.onFirstPage
        if onLaterPages is _doNothing and hasattr(self,'onLaterPages'):
            self.pageTemplates[1].beforeDrawPage = self.onLaterPages
        BaseDocTemplate.build(self, flowables, canvasmaker=canvasmaker)        
        
class Report:
    def __init__(self, date=None, path=None):
        self.date = self.getMonday(date)
        
    def getMonday(self, date=None):
        #Work out the Monday for the week containing date. If full week hasn't passed show previous week.
        today = ''
        if date == None:
            today = datetime.date.today()
        else:
            today = datetime.datetime(*time.strptime(date, "%Y-%m-%d")[0:5])
        if today.weekday() == 0:
            return today - datetime.timedelta(weeks=1)
        else:
            return today - datetime.timedelta(weeks=1, days=today.weekday())
        
    def getStyle(self):
        style = StyleSheet1()
        
        style.add(ParagraphStyle(name='ReportTitle',
                 spaceBefore = 0,
                 fontName='Helvetica',
                 fontSize=30,
                 leading=36,
                 textColor='#000000',
                 alignment=TA_CENTER)
        )
    
        style.add(ParagraphStyle(name='ReportTitleDate',
                 fontName='Helvetica',
                 fontSize=16,
                 leading=20,
                 textColor='#000000',
                 alignment=TA_CENTER)
        )
    
        style.add(ParagraphStyle(name='ReportSubTitle',
                 fontName='Helvetica',
                 fontSize=24,
                 leading=30,
                 textColor='#000000',
                 alignment=TA_CENTER)
        )

        style.add(ParagraphStyle(name='SectionTitle',
                 parent=style['ReportSubTitle'],
                 fontSize=18,
                 leading=24,
                 alignment=TA_LEFT)
        )    
            
        style.add(ParagraphStyle(name='Normal',
                 fontName='Helvetica',
                 fontSize=14,
                 leading=16,
                 textColor='#000000',
                 alignment=TA_LEFT)
        )
        
        style.add(ParagraphStyle(name='TableHeader',
                 fontName='Helvetica',
                 fontSize=14,
                 leading=16,
                 textColor='#000000',
                 alignment=TA_CENTER)
        )
                   
        style.add(ParagraphStyle(name='TableMain',
                 fontName='Helvetica',
                 fontSize=12,
                 leading=14,
                 wordWrap = 'para',
                 textColor='#000000',
                 alignment=TA_JUSTIFY)
        )
                   
        style.add(ParagraphStyle(name='TableMain_cent',
                 fontName='Helvetica',
                 fontSize=12,
                 leading=14,
                 wordWrap = 'para',
                 textColor='#000000',
                 alignment=TA_CENTER)
        )
         
        style.add(ParagraphStyle(name='Preformatted',
                 fontName='Courier',
                 fontSize=12,
                 leading=14,
                 textColor='#000000',
                 alignment=TA_LEFT)
        )
        
        style.add(ParagraphStyle(name='Footer',
                 fontName='Helvetica-Oblique',    # Fonts on page 24
                 fontSize=12,
                 leading=12,
                 textColor='#000000',
                 alignment=TA_RIGHT)
        )
        
        style.add(ParagraphStyle(name='Normal_just',
                                 parent=style['Normal'],
                                 alignment=TA_JUSTIFY))
        
        style.add(ParagraphStyle(name='Normal_cent',
                                 parent=style['Normal'],
                                 alignment=TA_CENTER))
        
        style.add(ParagraphStyle(name='Normal_just_rind',
                                 parent=style['Normal_just'],
                                 rightIndent=20))
        
        return style

    def getDate(self):
        day = self.date.strftime('%d')
        stndrdth = 'th'
        if day > 3 and day < 21:
            stndrdth = 'th'
        elif day[-1] == 1:
            stndrdth = 'st'
        elif day[-1] == 2:
            stndrdth = 'nd'
        elif day[-1] == 3:
            stndrdth = 'rd' 
        return "".join([self.date.strftime("%A %d<sup>"), stndrdth, self.date.strftime("</sup> %B, %Y")])

    def getQuarter(self):
        from datetime import date
        now = date.today()
        year = now.year
        quarter = 0
        for i in xrange(0, 4, 1):
            if now.month in xrange ((3*i) + 1, 1 + (3*(1+i)), 1):
                quarter = i + 1
        return (quarter, year)
        
        
        
        
        
        
        
        