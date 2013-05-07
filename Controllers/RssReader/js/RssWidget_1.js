
YAHOO.namespace ("webtools");

YAHOO.webtools.FeedsReader = function (el, userConfig) {
	if (arguments.length > 0) {
		YAHOO.webtools.FeedsReader.superclass.constructor.call(this, el, userConfig);
		}
	}

YAHOO.extend(YAHOO.webtools.FeedsReader, YAHOO.widget.Module);

// Define public variables to store ajax request paramethers
YAHOO.webtools.FeedsReader.CONFIG_SETUP_URL = "";
YAHOO.webtools.FeedsReader.FEEDS_SOURCE_URL = "";
YAHOO.webtools.FeedsReader.DEFAULT_FEEDS_NUMBER = 0;
YAHOO.webtools.FeedsReader.DEFAULT_FEEDS_FREQUENCY = 0;
YAHOO.webtools.FeedsReader.SETUP_PARAMETHERS = {feedsNumber: null, feedsFrequency: null};
YAHOO.webtools.FeedsReader.FEEDS_REQUEST_TRANSACTION = null;
YAHOO.webtools.FeedsReader.SETUP_REQUEST_TRANSACTION = null;



// Global variable for ajax reponse handling
YAHOO.webtools.FeedsReader.AJAX_FEEDS_REQUEST = {
	handleSuccess: function (o)
	{	
		var feeds = this.atomParser(o.responseXML);
		this.setOutput(feeds);
	},
	handleFailure: function (o)
	{
		alert("configuration request failed: "+o.statusText);	//o.getAllResponseHeaders
		//this.output = "invalid XML:<br /><br />"+o.statusText+"<br /><br />"+o.responseText.split('<').join("&lt;").split('>').join("&gt;");		
	},
	atomParser: function (atom)
	{
		var feeds = new Array();
	    var entries = atom.getElementsByTagName("entry");

        // Workaround to leverage the differences between safari and firefox.
        var hack_hasInnerText = (document.getElementsByTagName("body")[0].innerText != undefined) ? true : false;
       var hack_getText =  function (element)
        {
            if(!hack_hasInnerText)
            {
                return element.textContent;
            } else{
                return element.innerHTML;
            }
        }
		
		for(var i = 0; i < entries.length; i++) 
		{
			var entry = entries[i];
			var feed = new Object();

			//feed.title = entry.getElementsByTagName ("title")[0].textContent;
			//feed.content = entry.getElementsByTagName ("content")[0].textContent;
			//feed.updated = entry.getElementsByTagName ("updated")[0].textContent;
			//feed.link = entry.getElementsByTagName ("link")[0].getAttribute ("href");
			
			for (var j=0; j<entry.childNodes.length; j++) {
				if(entry.childNodes[j].nodeName=="title") {feed.title=entry.childNodes[j].firstChild.nodeValue;}
				if(entry.childNodes[j].nodeName=="content") {feed.content=entry.childNodes[j].getElementsByTagName("div")[0].innerHTML;}
				if(entry.childNodes[j].nodeName=="updated") {feed.updated=entry.childNodes[j].firstChild.nodeValue;}
				if(entry.childNodes[j].nodeName=="link") {feed.link=entry.childNodes[j].getAttribute("href");}
				}
				
			feeds.push(feed);
		}
		
		return feeds;
	},
	setOutput: function (feeds)
	{
		var output = '';	// contain the output
		for(var i = 0; i<feeds.length; i++) {	// foreach element in FR
				var output_tmp = '';
				for(j in feeds[i]) {	// foreach attribute in a given FR element
					// convert the attribute value to a string
					var s = new String(feeds[i][j]);	
					//filter for the link and update attribute
					if (j.indexOf('link') >= 0 || j.indexOf('updated') >= 0) continue; 
					// filter the method and empty value
					if(s.indexOf("function") < 0 && s != "") {	
						//title
						if (j.indexOf('title') >= 0) 
						    // write attribute value
							output_tmp += "<div>"+"<img src='../RssReader/css/plus.png' alt='' title='read more' id=\'"+i+"\' class='feedimg' /> " 
							              + s + "</div>";	
						else	//content
							output_tmp += "<div id=\'"+j+"_"+i+"\' class='feedcontent'> " + s + "</div>";
						}
					}
				var pattern = /\S*/i;	// is not empty
				if(pattern.test(output_tmp)) {
					output +="<div class='feedcontainer'>"+output_tmp+"</div><br /><br />";
					} 
			}
		
		
		this.module.setBody(output);
		this.module.render(YAHOO.util.Dom.getElementsByClassName ("bd", "div", this.root)[0]);
		
		var imgs = YAHOO.util.Dom.getElementsByClassName ("feedimg", "img", this.root);
		for(var j = 0; j<imgs.length; j++){
			var parent = imgs[j].parentNode.parentNode;
			YAHOO.util.Event.addListener(imgs[j], "click", this.toggleItem, parent, true);
			}
	},
	toggleItem: function (e)
	{
		var img = e.target;
		var root = img.parentNode.parentNode;
		var e = YAHOO.util.Dom.getElementsByClassName("feedcontent", "div", root)[0];
	
		if(img.src.indexOf("minus.png") >= 0) {
			img.src="../RssReader/css/plus.png";
			e.style.display="none";
			}
		else {
			img.src="../RssReader/css/minus.png";
			e.style.display="block";
			}
			
		var feeds = YAHOO.util.Dom.getElementsByClassName("feedcontainer", "div", root.parentNode);
	
		
		for (var i=0; i<feeds.length; i++){
			var parent = feeds[i];
			if(parent !== root) {
				var imgToClose = YAHOO.util.Dom.getElementsByClassName("feedimg", "img", parent)[0];
				var divToClose = YAHOO.util.Dom.getElementsByClassName("feedcontent", "div", parent)[0];
				imgToClose.src="../RssReader/css/plus.png";
				divToClose.style.display="none";
				}
			}				
	},
	module: null,
	root: null
};


YAHOO.webtools.FeedsReader.AJAX_SETUP_REQUEST = {
	handleSuccess: function (o)
	{
		if (this.params instanceof Array) {
			this.root.cfg.setProperty("feedsNumber",this.params[0]);
			this.root.cfg.setProperty("feedsFrequency",this.params[1]);
			}
		else this.test();
		
		alert(o.responseText.toString());
		
		this.root.cfg.refresh();
	},
	handleFailure: function (o)
	{ 
		alert("configuration request failed: "+o.statusText);	//o.getAllResponseHeaders
		//alert(o.responseText);
	},
	params: null,
	root: null,
	test: function () {alert(this.params+"\n"+this.root.element.className);}
};


		
// Presentation layers definition
YAHOO.webtools.FeedsReader.CSS_FEEDSREADER = "frWidget";
YAHOO.webtools.FeedsReader.CSS_DASHBOARDWIDGET = "DashboardWidget";


// Structure layers definition

YAHOO.webtools.FeedsReader.frNumberSelectDefaultOptions = ''+
						'<option value="1">1</option>'+
						'<option value="2">2</option>'+
						'<option value="3">3</option>'+
						'<option value="4">4</option>'+
						'<option value="5">5</option>'+
						'<option value="6">6</option>'+
						'<option value="7">7</option>'+
						'<option value="8">8</option>'+
						'<option value="9">9</option>'+
						'';
YAHOO.webtools.FeedsReader.frFrequencySelectDefaultOptions = ''+
							'<option value="1">1h</option>'+
							'<option value="6">6h</option>'+
							'<option value="12">12h</option>'+
							'<option value="24">24h</option>'+
													'';
YAHOO.webtools.FeedsReader.HEADER_HTML = '' +
					'<b class="rtop"><b class="r1"></b> <b class="r2"></b> <b class="r3"></b> <b class="r4"></b></b>'+
					'<div class="frWidgetTitleContainer">'+
					'<div class="frWidgetTitle">FEEDS READER</div>'+
					'<img src="../RssReader/css/setup.png" alt="" title="click and customize your feed aggregator" class="frWidgetToggleSetup" />'+
					'</div>'+
					'<div class="frWidgetSetup">'+
					'<form class="frWidgetSetupForm">'+
					'<select class="frWidgetNumberSelect">'+
					YAHOO.webtools.FeedsReader.frNumberSelectDefaultOptions+
					'</select> elements&nbsp;&nbsp;&nbsp;'+
					'<select class="frWidgetFrequencySelect">'+
					YAHOO.webtools.FeedsReader.frFrequencySelectDefaultOptions+
					'</select> refresh&nbsp;&nbsp;&nbsp;'+
					'<input type="submit" value="save" class="frWidgetSaveSetup" />&nbsp;'+
					'<input type="button" value="cancel" class="frWidgetCancelSetup" />'+
					'</form>'+
					'</div>'+
					'';
YAHOO.webtools.FeedsReader.BODY_HTML = '';
YAHOO.webtools.FeedsReader.FOOTER_HTML = '';

YAHOO.webtools.FeedsReader.OUTPUT_MODULE = null;

// Initialization & behaviour definition
YAHOO.webtools.FeedsReader.prototype.init = function(el, userConfig) {
	
	YAHOO.webtools.FeedsReader.superclass.init.call(this, el);
	
	this.beforeInitEvent.fire(YAHOO.webtools.FeedsReader);
	
	YAHOO.util.Dom.addClass(this.element, YAHOO.webtools.FeedsReader.CSS_FEEDSREADER);
	YAHOO.util.Dom.addClass(this.element, YAHOO.webtools.FeedsReader.CSS_DASHBOARDWIDGET);

	if (userConfig) {
		this.cfg.applyConfig(userConfig, true);
		}

    this.setHeader(YAHOO.webtools.FeedsReader.HEADER_HTML);
    this.setBody(YAHOO.webtools.FeedsReader.BODY_HTML);
    this.setFooter(YAHOO.webtools.FeedsReader.FOOTER_HTML);
				
	this.renderEvent.subscribe( function() {
		
		var root = this.element;
		
		//Initialization & global variabels set up

		if(!this.cfg.getProperty("setupURL")) this.cfg.setProperty("setupURL","frConfigModule.php");
		if(!this.cfg.getProperty("feedsURL")) this.cfg.setProperty("feedsURL","globalStatus.xml");

		//frWidgetSetUp Form INITIALIZATION EVENTS LISTENERS
		
		var frSetup = YAHOO.util.Dom.getElementsByClassName ("frWidgetSetup","div",root)[0];
		frSetupModule = new YAHOO.widget.Module(frSetup, { visible:false });
		frSetupModule.render();
		
		if(!this.cfg.getProperty("feedsNumber")) this.cfg.setProperty("feedsNumber",3);
		if(!this.cfg.getProperty("feedsFrequency")) this.cfg.setProperty("feedsFrequency",6);
		
		var frSave = YAHOO.util.Dom.getElementsByClassName ("frWidgetSaveSetup","input",root)[0];
		var frCancel = YAHOO.util.Dom.getElementsByClassName ("frWidgetCancelSetup","input",root)[0];
		var frToggle = YAHOO.util.Dom.getElementsByClassName ("frWidgetToggleSetup","img",root)[0];
		var frNumber = YAHOO.util.Dom.getElementsByClassName ("frWidgetNumberSelect","select",root)[0];
		var frFrequency = YAHOO.util.Dom.getElementsByClassName ("frWidgetFrequencySelect","select",root)[0];
		
		YAHOO.util.Event.addListener(frSave, "click", frSetupModule.hide, frSetupModule, true);
		YAHOO.util.Event.addListener(frSave, "click", this.setupSubmit, this, true);
		YAHOO.util.Event.addListener(frCancel, "click", frSetupModule.hide, frSetupModule, true);
		YAHOO.util.Event.addListener(frCancel, "click", this.setupCancel, this, true);
		YAHOO.util.Event.addListener(frToggle, "click", this.setupToggle, frSetupModule, true);

		}, this, true);
		
	this.initEvent.fire(YAHOO.webtools.FeedsReader);
	};


// Default config

YAHOO.webtools.FeedsReader.prototype.initDefaultConfig = function ()
{
    YAHOO.webtools.FeedsReader.superclass.initDefaultConfig.call (this);
    
    this.cfg.addProperty ("feedsURL", {handler:this.configFeedsRequest, suppressEvent: true});
    this.cfg.addProperty ("setupURL", {handler:this.configSetupRequest, suppressEvent: true});
    this.cfg.addProperty ("feedsNumber", {handler:this.configFeedsNumber, suppressEvent:true});
    this.cfg.addProperty ("feedsFrequency", {handler:this.configFeedsFrequency, suppressEvent:true});
	
};

YAHOO.webtools.FeedsReader.prototype.configFeedsRequest = function (type, args, obj)
{
   	this.FEEDS_SOURCE_URL = args[0];
	
	var feedsSourceURL = args[0];

	var ajaxRequest = YAHOO.webtools.FeedsReader.AJAX_FEEDS_REQUEST;
	
	var root = this.element;
	
	if (document.getElementById(root.id+"_output")) {
		//alert("riga 276");
		var oldModule = document.removeNode(root.id+"_output");
		var parent = oldModule.parentNode;
		parent.removeChild(oldModule);
		}
		
	var frOutputModule = new YAHOO.widget.Module(root.id+"_output");
	ajaxRequest.module = frOutputModule;
	ajaxRequest.root = root;
		
	var callback = 
	{
		success: ajaxRequest.handleSuccess,
		failure: ajaxRequest.handleFailure,
		scope: ajaxRequest,
		timeout: 10000
	};

	//this.FEEDS_REQUEST_TRANSACTION
	var transaction = YAHOO.util.Connect.asyncRequest("GET",feedsSourceURL,callback, null);
   
};

YAHOO.webtools.FeedsReader.prototype.configSetupRequest = function (type, args, obj)
{
	this.CONFIG_SETUP_URL = args[0];
};

YAHOO.webtools.FeedsReader.prototype.configFeedsNumber = function (type, args, obj)
{
	this.DEFAULT_FEEDS_NUMBER = args[0];
	
	var i = args[0];
	var root = this.element;
	var selectControl = YAHOO.util.Dom.getElementsByClassName ("frWidgetNumberSelect","select",root)[0];
	var selectOptions = selectControl.getElementsByTagName("option");
	for (var k = 0; k<selectOptions.length; k++) {
		if (k == i-1) selectOptions[k].selected="selected"; //selectOptions[k].setAttribute("selected","selected");
		else if(selectOptions[k].selected) selectOptions[k].removeAttribute("selected");
		}
	
};

YAHOO.webtools.FeedsReader.prototype.configFeedsFrequency = function (type, args, obj)
{
	this.DEFAULT_FEEDS_FREQUENCY = args[0];
	
	var i = args[0]+'';
	var root = this.element;
	var selectControl = YAHOO.util.Dom.getElementsByClassName ("frWidgetFrequencySelect","select",root)[0];
	var selectOptions = selectControl.getElementsByTagName("option");
	for (var k = 0; k<selectOptions.length; k++) {
		if (selectOptions[k].value == i) selectOptions[k].selected="selected";
		else if(selectOptions[k].selected) selectOptions[k].removeAttribute("selected");
		}
};



// My customized methods


// Managing and showing the parsed result

YAHOO.webtools.FeedsReader.prototype.setupSubmit = function (e, obj)
{		
	var setupURL = obj.cfg.getProperty("setupURL");
	
	var root = obj.element;
	
	var selectControlFrequency = YAHOO.util.Dom.getElementsByClassName ("frWidgetFrequencySelect","select",root)[0];
	var selectControlNumber = YAHOO.util.Dom.getElementsByClassName ("frWidgetNumberSelect","select",root)[0];
	
	var ajaxRequest = YAHOO.webtools.FeedsReader.AJAX_SETUP_REQUEST;
	ajaxRequest.root = obj;
	ajaxRequest.params = [selectControlNumber.value,selectControlFrequency.value];
	
	var callback =
	{
		success: ajaxRequest.handleSuccess,
		failure: ajaxRequest.handleFailure,
		scope: ajaxRequest,
		timeout: 10000
	};
	
	alert("frConfigModule.php?feedsNumber="+ajaxRequest.params[0]+"&feedsFrequency="+ajaxRequest.params[1]);
	//this.SETUP_REQUEST_TRANSACTION 
	var transaction = YAHOO.util.Connect.asyncRequest("POST", "frConfigModule.php", callback,"feedsNumber="+ajaxRequest.params[0]+"&feedsFrequency="+ajaxRequest.params[1]);
	
	// restart feeds ajax request
}

YAHOO.webtools.FeedsReader.prototype.setupCancel = function (e,obj)
{
	this.DEFAULT_FEEDS_NUMBER = obj.cfg.getProperty("feedsNumber");
	this.DEFAULT_FEEDS_FREQUENCY = obj.cfg.getProperty("feedsFrequency");
	
	//var n = this.cfg.getProperty("feedsNumber");
	obj.cfg.setProperty("feedsNumber",3); //alert(this.cfg.getProperty("feedsNumber"));
	
	//var f = this.cfg.getProperty("feedsFrequency");
	obj.cfg.setProperty("feedsFrequency",6); //alert(this.cfg.getProperty("feedsFrequency"));
}


YAHOO.webtools.FeedsReader.prototype.setupToggle = function (e)
{
	if(frSetupModule.cfg.getProperty("visible")) frSetupModule.hide();
	else frSetupModule.show();
}


