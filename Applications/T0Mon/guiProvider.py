from globals import logger
from globals import debugPrintQueries
import config
from consts import *
from utils import *
from string import replace

### Module for generating HTML gui ###
 
def getDoubleTableGui(id, td, pageMenuLen = 50):
    """
    Returns table GUI for TableData for a table with 2 levels of columns
    """
    table = ""
    table += '<table border="0" cellspacing="2">\n'

    # build title

    table += '<tr>'
    table += '<th colspan="' + str(td.cols.getTotalNumSubCols()) + '">' + td.title + " ["
    if hasattr(td, "dataCount"):
        table += 'count=' + str(td.dataCount) + ', '
    else:
        table += 'count=' + str(len(td.data)) + ', '
    table += "query=" + str(int(td.qtime)) + "ms"
    if td.atime > 10:
        table += ', analysis=' + str(int(td.atime)) + "ms"
    table += "]</th>"
    table += '</tr>\n'

    # build paging

    if hasattr(td, "dataCount"):
        all = "All "
        if td.dataCount > td.pageSize:
            table += '<tr>\n'
            table += '<td colspan="' + str(td.cols.getTotalNumSubCols()) + '">'
            if td.page != None:
                table += '<a href="' + formGetParameters({id + "_p" : "all"}) + '">'
            table += all
            if td.page != None:
                table += '</a>'
            r = td.dataCount / td.pageSize
            if td.dataCount % td.pageSize != 0:
                r += 1
            numchars = len(all)
            for i in range(r):
                if i != td.page:
                    table += '<a href="' + formGetParameters({id + "_p" : i}) + '">'
                caption = str(i + 1) + " "
                table += caption
                numchars += len(caption)
                if i != td.page:
                    table += "</a>"
                if numchars >= pageMenuLen:
                    table += "<br />"
                    numchars = 0
            table += '</td>\n'
            table += '</tr>\n'

    # Build Orderby and Col names

    # First level: Main columns
    
    table += "<tr>"
    for i in range(0, td.cols.getNumMainCols()):
        colspan = td.cols.getNumSubColsIn(i)
        if colspan == 0: colspan = 1
        table += '<th colspan=' + str(colspan)  + '>'
        table += str(td.cols.getMainCol(i).title)
       
        if (td.cols.getMainCol(i).info != None):
            if i == 0:
                table += buildTooltip(td.cols.getMainCol(i).info, width=200, pos=0)
            elif i == len(td.cols) - 1:
                table += buildTooltip(td.cols.getMainCol(i).info, width=200, pos=-200)
            else:
                table += buildTooltip(td.cols.getMainCol(i).info, width=200, pos=-100)
        table += "</th>"
    table += "</tr>\n"

    # Second level: Subcolumns
    
    table += "<tr>"
    for i in range(0, td.cols.getNumMainCols()):
        if td.cols.getNumSubColsIn(i) == 0:
            table += '<td style="background-color:#b9d0de">'
            table += "</td>"
        else:
            for j in range(0, td.cols.getNumSubColsIn(i)):
                table += '<td style="background-color:#b9d0de">'
                if td.cols.getSubCol(i,j).visible == True:
		    table += replace(td.cols.getSubCol(i,j).title, " ", "&nbsp;")
   	            if (td.cols.getSubCol(i,j).info != None):
		        if i == 0:
        	            table += buildTooltip(td.cols.getSubCol(i,j).info, width=200, pos=0)
		        elif i == len(td.cols) - 1:
	                    table += buildTooltip(td.cols.getSubCol(i,j).info, width=200, pos=-200)
	        	else:
		            table += buildTooltip(td.cols.getSubCol(i,j).info, width=200, pos=-100)
                table += "</td>"
    table += "</tr>"
  

    # Build body

    start = 0 * config.PAGE_SIZE;
    for k in range(0, len(td.data)):
        table += "<tr>"
        cell = 0
        for i in range(0, td.cols.getNumMainCols()):
            if td.cols.getNumSubColsIn(i) == 0:
                table += '<td'
                if (k % 2 == 0):
                    table += ' style="background-color:white"'
                table += '>'
                if td.data[k][cell] != None:
                    if td.cols.getMainCol(i).decorator != None:
                        table += str(td.cols.getMainCol(i).decorator(td.data[k][cell]))
                    else:
                        table += str(td.data[k][cell])
                table += "</td>"
                cell += 1
            else:
                for j in range(0, td.cols.getNumSubColsIn(i)):
                    table += '<td'
                    if (k % 2 == 0):
                        table += ' style="background-color:white"'
                    table += ">"
                    if td.cols.getSubCol(i,j).visible == True and td.data[k][cell] != None:
                        if td.cols.getSubCol(i,j).decorator != None:
                            table += str(td.cols.getSubCol(i,j).decorator(td.data[k][cell]))
                        else:
                            table += str(td.data[k][cell])
                    table += "</td>"
                    cell += 1
        table += "</tr>"        

    table += "</table>"
    table+=readQuery(td)
    return table



def getTableGui(id, td, pageMenuLen = 50):
    """
    Returns table GUI for TableData
    """
    table = ""
    table += '<table border="0" cellspacing="2">\n'

    # build title

    table += '<tr>'
    table += '<th colspan="' + str(len(td.cols)) + '">' + td.title + " ["
    if hasattr(td, "dataCount"):
        table += 'count=' + str(td.dataCount) + ', '
    else:
        table += 'count=' + str(len(td.data)) + ', '
    table += "query=" + str(int(td.qtime)) + "ms"
    if td.atime > 10:
        table += ', analysis=' + str(int(td.atime)) + "ms"
    table += "]</th>"
    table += '</tr>\n'

    # build paging

    if hasattr(td, "dataCount"):
        all = "All "
        if td.dataCount > td.pageSize:
            table += '<tr>\n'
            table += '<td colspan="' + str(len(td.cols)) + '">'
            if td.page != None:
                table += '<a href="' + formGetParameters({id + "_p" : "all"}) + '">'
            table += all
            if td.page != None:
                table += '</a>'
            r = td.dataCount / td.pageSize
            if td.dataCount % td.pageSize != 0:
                r += 1
            numchars = len(all)
            for i in range(r):
                if i != td.page:
                    table += '<a href="' + formGetParameters({id + "_p" : i}) + '">'
                caption = str(i + 1) + " "
                table += caption
                numchars += len(caption)
                if i != td.page:
                    table += "</a>"
                if numchars >= pageMenuLen:
                    table += "<br />"
                    numchars = 0
            table += '</td>\n'
            table += '</tr>\n'

    # Build Orderby and Col names

    table += "<tr>"
    for i in range(0, len(td.cols)):
        if not td.cols[i].visible: continue
        table += '<td style="background-color:#b9d0de">'
        if td.orderby == i:
            if td.asc == True:
                table += '<img src="/' + PROJECT_NAME + '/images/orderasc.png" alt="" />'
            else:
                table += '<img src="/' + PROJECT_NAME + '/images/orderdesc.png" alt="" />'
        table += '<a href="'
        value = str(i) + "_"
        if td.orderby == i :
            value += str(not td.asc)
        else:
            value += str(False)
        params = {}
        params[id] = value
        table += formGetParameters(params)
        table += '">' \
            + str(td.cols[i].title) \
            + "</a>"
        if (td.cols[i].info != None):
            if i == 0:
                table += buildTooltip(td.cols[i].info, width=200, pos=0)
            elif i == len(td.cols) - 1:
                table += buildTooltip(td.cols[i].info, width=200, pos=-200)
            else:
                table += buildTooltip(td.cols[i].info, width=200, pos=-100)
        table += "</td>"
    table += "</tr>\n"

    # Build body

    start = 0 * config.PAGE_SIZE;
    for j in range(len(td.data)):
        if (j >= len(td.data)): break;
        table += "<tr>"
        for i in range(0, len(td.cols)):
            if not td.cols[i].visible: continue
            cell = td.data[j][i]
            if td.cols[i].decorator != None:
                cell = td.cols[i].decorator(cell)
            table += "<td "
            if (j % 2 == 0):
                table += 'style="background-color:white"'
            table += ">" + str(cell) + "</td>"
        table += "</tr>\n"
        j += 1

    table += "</table>"
    table += readQuery(td)
    return table

def getVertTableGui(id, td):
    """
    Returns table GUI for TableData where data rows are vertical
    """
    table = ""
    table += '<table border="0">\n'
    table += '<tr>'
    table += '<th colspan="' + str(len(td.data) + 1) + '">' + str(td.title) + " " + "[" + str(int(td.qtime)) + "ms]" + "</th>"
    table += '</tr>\n'

    for i in range(len(td.cols)):
        table += "<tr>"
        table += "<td "
        if (i % 2 == 0):
            table += 'style="background-color:white"'
        table += ">" + td.cols[i].title + "</td>"
        for j in range(len(td.data)):
            if (i < len(td.data[j])):
                table += "<td "
                if (i % 2 == 0):
                    table += 'style="background-color:white"'
                cell = td.data[j][i]
                if td.cols[i].decorator != None:
                    cell = td.cols[i].decorator(cell)
                table += ">" + str(cell) + "</td>"
        table += "</tr>"

    table += "</table>"
    table+=readQuery(td)
    
    return table

def readQuery(td):
	if debugPrintQueries==False: return ""
	res=""
	if hasattr(td, "query"):
		query = td.query
	elif hasattr(td, "mainQuery"):
		query = td.mainQuery
	else: query="" 
	if query != "":
	  res= """<form>
	<input type="button" onclick=
	"alert('""" + str(query).replace("\"","").replace("\'","\\\'").replace("\n","\\n").replace("   "," ")+"""')" value="Read Query">
</form>"""
	
	return res