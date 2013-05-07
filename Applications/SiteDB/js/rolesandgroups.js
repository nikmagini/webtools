function GetGroups(base){
	var sUrl = base + "/json/index/Groups/";
	var callback = {
    success: function (o) {
    	var obj = eval("(" + o.responseText + ")");
			var str = "";
			
			for (i in obj){
				str += "<li class='small grouplist'><a href='" + base + "/rolesandgroups/showgroup/" + obj[i]['name'] + "'>" + obj[i]['name'] + "</a></li>"; 
			}
			var elem = document.getElementById("grouplist");
			if (elem) {elem.innerHTML = str};
    },
    failure: function (o) {
    //do nothing
    }
   }
	var request = YAHOO.util.Connect.asyncRequest('GET', sUrl, callback);
}

function GetRoles(base, group){
	var sUrl = base + "/json/index/RolesForGroup?group=" + group;
	var callback = {
    success: function (o) {
    	var obj = eval("(" + o.responseText + ")");
			var str = "";
			for (i in obj){
				str += "<div id='rolelist_" + obj[i]['title'] + "'>";
				str += "<h3>" + obj[i]['title'] + "</h3>";
				str += "</div>";
				GetPeopleWithRoleInGroup(base, group, obj[i]['title'], "rolelist_" + obj[i]['title']);
			}
			var elem = document.getElementById("rolelist");
			if (elem) {elem.innerHTML = str};
    },
    failure: function (o) {
    //do nothing
    }
   }
	var request = YAHOO.util.Connect.asyncRequest('GET', sUrl, callback);
}

function GetPeopleWithRoleInGroup(base, group, role, element){
	var sUrl = base + "/json/index/PeopleWithRoleInGroup?group=" + group + "&role=" + role;
	var callback = {
    success: function (o) {
    	var obj = eval("(" + o.responseText + ")");
			var str = "";
			for (i in obj){
				str += "<p><a href='mailto:" + obj[i]['email'] + "'>" + obj[i]['forename'] + " " + obj[i]['surname'] + "</a> - identified by <b>" + obj[i]['username'] + "</b> <i>(" + obj[i]['DN'] + ")</i></p>";
			}
			var elem = document.getElementById(element);
			if (elem) {elem.innerHTML += str};
    },
    failure: function (o) {
    //do nothing
    }
   }
	var request = YAHOO.util.Connect.asyncRequest('GET', sUrl, callback);
}