from time import *
from sqlalchemy import Table
import sys
import traceback

import globals
from consts import *

### Module for short functions that did not fit anywhere else ###
### Probably it is a good idea to move them somewhere else some day ###

def Tbl(tableName, stringFormat=False):
    """
    Returns sqlalchemy Table for tableName if stringFormat == False
    Otherwise returns a string formed from DB schema and tableName
    """
    if config.DB_SCHEMA != "":
        if stringFormat == False:
            return Table(tableName, globals.dbMeta, autoload = True, schema = config.DB_SCHEMA)
        else:
            return config.DB_SCHEMA + '.' + tableName
    else:
        if stringFormat == False:
            return Table(tableName, globals.dbMeta, autoload = True)
        else:
            return tableName
 
def buildExpressLink(id):
    return buildSimpleLink('express', id)

def buildExpressMergeLink(id):
    return buildSimpleLink('expressMerge', id)

def buildExpressJobLink(id):
    return buildSimpleLink('expressJob', id)

def buildExpressMergeJobLink(id):
    return buildSimpleLink('expressMergeJob', id)



def buildRepackLink(id):
    return buildSimpleLink('repack', id)

def buildRepackJobLink(id):
    return buildSimpleLink('repackJob', id)

def buildStreamerLink(id):
    return buildSimpleLink('streamer', id)

def buildRecoLink(id):
    return buildSimpleLink('reco', id)

def buildRecoMergeLink(id):
    return buildSimpleLink('recoMerge', id)

def buildRepackMergeLink(id):
    return buildSimpleLink('repackMerge', id)

def buildRepackMergeJobLink(id):
    return buildSimpleLink('repackMergeJob', id)

def buildRecoJobLink(id):
    return buildSimpleLink('recoJob', id)

def buildRecoMergeJobLink(id):
    return buildSimpleLink('recoMergeJob', id)

def buildAlcaSkimLink(id):
    return buildSimpleLink('alcaSkim', id)

def buildAlcaSkimMergeLink(id):
    return buildSimpleLink('alcaSkimMerge', id)

def buildAlcaSkimJobLink(id):
    return buildSimpleLink('alcaSkimJob', id)

def buildAlcaSkimMergeJobLink(id):
    return buildSimpleLink('alcaSkimMergeJob', id)

def buildExpressMergeJobLink(id):
    return buildSimpleLink('expressMergeJob', id)

def buildSimpleLink(object, id):
    return '<a href="/' + PROJECT_NAME + '/' + str(object) + '/' + str(id) + '/">' \
        + str(id) + '</a>'

def buildWebLink(object):
    linkLen = 40
    if object == None: return ""
    if len(object) > linkLen: 
	return '<a href="' + object + '" alt="'+ object  +'">...' + object[-linkLen:] + '</a>'
    else:
	return '<a href="' + object + '" alt="'+ object  +'">' + object + '</a>'

def buildLeftStrip( object ):
    fieldWidth = 20
    wordWidth = fieldWidth - 3
    if len(object) <= fieldWidth:
        return object
    else:
        return buildTooltip( object, width=400, object='...' + object[-wordWidth:] )

def wrapInBorder(object):
    """ Add border to HTML object """
    borderedObject = '<table style="border:5px solid blue;"><tr><td style="text-align:center">' + str(object) + '</td></tr></table>'
    return borderedObject

def formatPercentage(num, percentage):
    """ Create percentage bar """
    if percentage.percentage == 0:
        width = 100
    elif percentage.percentage == 100 and percentage.value == 0:
        width = 0
    else:
        width = percentage.percentage
    result = '<div style="width:' + str(width) + 'px;height:5px;background-color:'
    if percentage.percentage == 0:
        result += 'red'
    elif percentage.percentage == 100:
        result += 'green'
    else: result += 'yellow'
    result += '">'
    result += "</div>"
    result += str(num) + " (" + str(percentage.percentage) + "%)"
    return result

def formatDoublePercentage(firstN, firstP, secondN, secondP, tag1, tag2):
    """Create a set of percentages bar"""
    bar = ""
    if firstP.percentage == 0:
	firstWidth = 100
    elif firstP.percentage == 100 and firstP.value == 0:
	firstWidth = 0 # a 0
    else:
	firstWidth = firstP.percentage
    if secondP.percentage == 0:
        secondWidth = 100
    elif secondP.percentage == 100 and secondP.value == 0:
        secondWidth = 0 # a 0
    else:
        secondWidth = secondP.percentage
    
    bar = '<div style="width:' + str(firstWidth) + 'px;height:5px;background-color:'
    if firstP.percentage == 0:
        bar += 'red'
    elif firstP.percentage == 100:
        bar += 'green'
    else: bar += 'yellow'
    bar += '">'
    bar += "</div>"

    bar += str(firstN) + " (" + str(firstP.percentage) + "% " + tag1 + ")"

    bar += '<div style="width:' + str(secondWidth) + 'px;height:5px;background-color:'
    if secondP.percentage == 0:
        bar += 'red'
    elif secondP.percentage == 100:
        bar += 'green'
    else: bar += 'yellow'
    bar += '">'
    bar += "</div>"

    bar += str(secondN) + " (" + str(secondP.percentage) + "% " + tag2  + ")"
    return bar

def formatMultiplePercentages(percentages):
    """percentages is an array containing arrays of this type [value, percentage, tag]"""
    bar = ""
    for i in range(len(percentages)):
	value = percentages[i][0]
	percentage = percentages[i][1]
	tag = percentages[i][2]
	
	if percentage.percentage == 0:
	    width = 100
	elif percentage.percentage == 100 and percentage.value == 0:
	    width = 0
	else:
	    width = percentage.percentage

	bar += '<div style="width:' + str(width) \
                + 'px;height:5px;background-color:'
	if percentage.percentage == 0:
	    bar += 'red'
	elif percentage.percentage == 100:
	    bar += 'green'
	else: bar += 'yellow'
	bar += '">'
	bar += "</div>"

    for i in range(len(percentages)):
	value = percentages[i][0]
	percentage = percentages[i][1]
	tag = percentages[i][2]
	
	bar += str(value) + ","

    bar = bar.rstrip(',')
    bar += " "

    for i in range(len(percentages)):
	value = percentages[i][0]
	percentage = percentages[i][1]
	tag = percentages[i][2]

        if percentage.percentage == 100:
            bar += "1,"
        else:
            bar += str(percentage.percentage)+ "%,"

    bar = bar.rstrip(',')

    return bar

def timeToClock(time):
    """
    Create clock icon with time value tooltip
    """
    time = formatTime(time)
    return buildTooltip(time, 130, 0, '<img src="/' + PROJECT_NAME + '/images/clock.png" alt="" style="border:0px"/>')

def formatTime(time):
    """
    Format time number to human readable format
    """
    t = localtime(time)
    t2 = []
    for i in range(0, len(t)):
        if t[i] < 10:
            t2.append("0" + str(t[i]))
        else:
            t2.append(str(t[i]))
    return t2[0] + "-" + \
            t2[1] + "-" + \
            t2[2] + " " + \
            t2[3] + ":" + \
            t2[4] + ":" + \
            t2[5]

def deltaTime(startTime):
    """
    Get time diference between startTime and now
    """
    delta = int(time()) - int(startTime)
    result = ""
    s = delta % 60
    delta /= 60
    result = str(s) + "s"
    if delta != 0:
        m = delta % 60
        delta /= 60
        result = str(m) + "m " + result
    if delta != 0:
        h = delta % 24
        delta /= 24
        result = str(h) + "h " + result
    if delta != 0:
        d = delta
        result = str(d) + "d " + result
    return result

def numToDateString(datenum):
    date = localtime(datenum)
    return str(date[0]) + "-" + str(date[1]) + "-" + str(date[2]) + \
        " " + str(date[3]) + ":" + str(date[4]) + ":" + str(date[5])

def buildTooltip(text, width=200, pos=-100, object=None):
    tooltip = '&nbsp;<a class="info" href="#">'
    if object == None:
        tooltip += '<img src="/' + PROJECT_NAME + '/images/info.png" alt="" style="border:0px"/>'
    else:
        tooltip += object
    tooltip += '<span style="'
    tooltip += 'width:' + str(width) + 'px;';
    tooltip += 'left:' + str(pos) + 'px;';
    tooltip += '">' + str(text) + '</span>'
    tooltip += '</a>'
    return tooltip

def formRunLink(runid):
    return '<a href="/' + PROJECT_NAME + '/run/' + str(runid) + '/">' + str(runid) + "</a>"

def formRepackJobTableLink(text, tableName, status, runid = None):
    if (runid == None): runParamString = ""
    else: runParamString = '&amp;runid=' + str(runid)
    return '<a href="/' + PROJECT_NAME + '/jobs/?table=' + tableName + '&amp;status=' + str(status) + runParamString + '">' + str(text) + '</a>'

def formJobTableLink(text, inputTier, mergeFlag, status, runid = None):	
    if inputTier != None:
	    option = 'inputTier=' + inputTier
    else: option = 'option=Express'
    if (runid == None): runParamString = ""
    else: runParamString = '&amp;runid=' + str(runid)
    return '<a href="/' + PROJECT_NAME + '/jobs/?'+option + '&amp;mergeFlag=' + mergeFlag + '&amp;status=' + status + runParamString + '">' + str(text) + '</a>'
    

def textToImageAlt(text):
    return '<a href="file://' + text + '"><img src="/' + PROJECT_NAME + '/images/doc.png" alt="" title="' + text + '" style="border:0px"/></a>'

def wrapTextArea(text, cols = 1, rows = 2):
    """
    Put text into text area
    """
    return '<textarea readonly="readonly" cols="' \
        + str(cols) + '" rows="' + str(rows) + '">' \
        + text + '</textarea>\n'

def humanFilesize(size):
    """
    Convert size in Bytes to more human readable format
    """
    if size < 1024:
        return ("%d B") % (size)
    elif size < (1024 * 1024):
        return ("%.2f KB") % (float(size) / (1024))
    elif size < (1024 * 1024 * 1024):
        return ("%.2f MB") % (float(size) / (1024 * 1024))
    else:
        return ("%.2f GB") % (float(size) / (1024 * 1024 * 1024))

def formGetParameters(nkwds = {}):
    """
    Build a string from current GET parameters and new keywords
    """
    if globals.pageParams == None:
        globals.pageParams = {}
    params = "?"
    for k in globals.pageParams.keys():
        if nkwds.has_key(k):
            params += str(k) + "=" + str(nkwds[k]) + "&amp;"
        else:
            params += str(k) + "=" + str(globals.pageParams[k]) + "&amp;"
    for k in nkwds.keys():
        if not globals.pageParams.has_key(k):
            params += str(k) + "=" + str(nkwds[k]) + "&amp;"
    return params

def formatExceptionInfo(maxTBlevel=100):
    """
    Get last exception info in HTML format
    """
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.__dict__["args"]
    except KeyError:
        excArgs = "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    return excName + "<br />" + \
        ''.join(str(a) + "<br />" for a in excArgs) + \
        ''.join(str(t) + "<br />" for t in excTb)
