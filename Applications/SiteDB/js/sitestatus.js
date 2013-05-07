function StatusUpdate(sArr, base){
	var sUrl = base + "/json/index/SiteStatus?";
	q = 0
	for (s in sArr) {
		if (q >0){
			sUrl += "&cms_name="+sArr[s];
		} else {
			sUrl += "cms_name="+sArr[s];
			q = 1
		}
	}	
	var callback = {
    success: function (o) {
    	var obj = eval("(" + o.responseText + ")");
			var str = base + "	/common/images/help.png";
			
			for (i in obj){
				var id = obj[i]['id'];
				if (obj[i]['status'] == "UP"){
					str = base + "/common/images/flag_green.png";
				} else if (obj[i]['status'] == "MAINTENANCE"){
					str = base + "/common/images/control_pause.png";
				} else if (obj[i]['status'] == "WARNING"){
					str = base + "/common/images/error.png";
				} else if (obj[i]['status'] == "ERROR"){
					str = base + "/common/images/exclamation.png";
				}
				var elem = document.getElementById("flag_"+ id);
				if (elem) {
					elem.src = str;
					elem.alt = obj[i]['status'];
				}
			}
    },
    failure: function (o) {
    //do nothing
    }
   }
	var request = YAHOO.util.Connect.asyncRequest('GET', sUrl, callback);
	
}

function loadMonitoring(s, base, endpoint){
	var sUrl = base + "/json/index/SitetoCMSName?name="+s;
	var callback = {
    success: function (o) {
			var obj = eval("(" + o.responseText + ")");
			var str = ''
			p = 0;
			var one_day=60*60*24;
			var today = new Date();
			var end = today.getTime() / 1000;
			var start = end - (7* one_day);
			for (i in obj){
				str = "<p>PhEDEx transfer rate to " + s + "<br/> <span class='small'>- click plot for larger version</span><br/>";
				str += "<a href='https://cmsdoc.cern.ch:8443/cms/aprom/phedex/prod/Activity::RatePlots?graph=quantity_rates&entity=link&src_filter=" + obj[i]['name'] + "&dest_filter=&no_mss=true&period=l7d&upto='>";
				str += "<img width='280' height='175' id='ratePlot' align='center' src='";
				str += "http://cmsdoc.cern.ch/cms/aprom/phedex/cgi-bin/phedex-cgi.sh?";
				str += "link=link&no_mss=true&conn=Prod/WebSite&from_node=" + obj[i]['name'];
				str += "&starttime=" + start + "&endtime=" + end + "&span=86400&graph=quantity_rates&legend=False&text_size=10";
				str += "'/>";
				str += "</a>";
				str += "</p>";
				str += "<p>" + s + " PhEDEx transfer quality<br/> <span class='small'>- click plot for larger version</span><br/>";
				str += "<a href='https://cmsdoc.cern.ch:8443/cms/aprom/phedex/prod/Activity::QualityPlots?graph=quality_all&entity=link&src_filter=" + obj[i]['name'] + "&dest_filter=&period=l7d&upto='>";
				str += "<img width='280' height='175' id='ratePlot' align='center' src='";
				str += "http://cmsdoc.cern.ch/cms/aprom/phedex/cgi-bin/phedex-cgi.sh?";
				str += "link=link&no_mss=true&conn=Prod/WebSite&from_node=" + obj[i]['name'];
				str += "&starttime=" + start + "&endtime=" + end + "&span=86400&graph=quality_all&legend=False&text_size=10";
				str += "'/>";
				str += "</a>";
				str += "</p>";
				p += 1
			}
			if (p == 0) {
				str += "<p><b>No PhEDEx node registered!</b></p>";
        str += "<p>Please update SiteDB with the <a href='https://savannah.cern.ch/support/?func=additem&group=cmscompinfrasup&category_id=108&severity=9&assigned_to=3534&summary=Missing PhEDEx Node at " + s +"'>PhEDEx node</a>.</p>";
			}
			var elem = document.getElementById("monitoring")
			if (elem) {elem.innerHTML = str}
    },
    failure: function (o) {
    //do nothing
    }
	}
	var request = YAHOO.util.Connect.asyncRequest('GET', sUrl, callback);
}