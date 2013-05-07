function SitetoName(s, base, type){
	var sUrl = base + "/json/index/Siteto" + type + "Name?name="+s;
	
	var callback = {
    success: function (o) {
    	var obj = eval("(" + o.responseText + ")");
			var str = 'unknown';
			p = 0;
			for (i in obj){
				if (p > 0) {
					str = str + ", " + obj[i]['name'];
				} else {
					str = obj[i]['name'];
				}
				p = p+1;
			}
			if (p > 1) {
				str = "<b>" + type + " Names:</b> " + str
			} else {
				str = "<b>" + type + " Name:</b> " + str
			}
			var elem = document.getElementById(type + "_NAME_text")
			if (elem) {elem.innerHTML = str}
    },
    failure: function (o) {
    //do nothing
    }
   }
	var request = YAHOO.util.Connect.asyncRequest('GET', sUrl, callback);
	
}

function CVSLink(s, base){
	var sUrl = base + "/json/index/SitetoCMSName?name="+s;
	var callback = {
    success: function (o) {
			var obj = eval("(" + o.responseText + ")");
			var str = '';
			p = 0;
			for (i in obj){
				str += "<a href='http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/COMP/SITECONF/" + obj[i]['name'] + "'>" + obj[i]['name'] + "</a><br/>"
			}
			var elem = document.getElementById("cvs")
			if (elem) {elem.innerHTML = str}
    },
    failure: function (o) {
    //do nothing
    }
	}
	var request = YAHOO.util.Connect.asyncRequest('GET', sUrl, callback);
	
}

function GstatLinks(s, base, gstat){
	var sUrl = base + "/json/index/SitetoSAMName?name="+s;
	
	var callback = {
    success: function (o) {
    	var obj = eval("(" + o.responseText + ")");
			var str = '';
			p = 0;
			for (i in obj){
				str += "<a href='" + gstat + "/" + obj[i]['name'] + "'>GSTAT</a><br/>"
			}
			var elem = document.getElementById("gstat")
			if (elem) {elem.innerHTML = str}
    },
    failure: function (o) {
    //do nothing
    }
   }
	var request = YAHOO.util.Connect.asyncRequest('GET', sUrl, callback);
}

function SquidLinks(s, base, squid){
	var sUrl = base + "/json/index/SitetoCMSName?name="+s;
	
	var callback = {
    success: function (o) {
    	var obj = eval("(" + o.responseText + ")");
			var str = '';
			p = 0;
			for (i in obj){
				str += "<a href='" + squid + "/" + obj[i]['name'] + "/proxy-hit.html'>Squid MRTG</a><br/>"
			}
			var elem = document.getElementById("squid")
			if (elem) {elem.innerHTML = str}
    },
    failure: function (o) {
    //do nothing
    }
   }
	var request = YAHOO.util.Connect.asyncRequest('GET', sUrl, callback);
}

function fillNamesText(s, base, gstat, squid){
	SitetoName(s, base, 'SAM')
	SitetoName(s, base, 'CMS')
	GstatLinks(s, base, gstat)
	SquidLinks(s, base, squid)
	CVSLink(s, base)
}