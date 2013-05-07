
YAHOO.namespace ("webtools");

YAHOO.webtools.FeedsReader = function (el, userConfig) {
	if (arguments.length > 0) {
		YAHOO.webtools.FeedsReader.superclass.constructor.call(this, el, userConfig);
		}
	}

YAHOO.extend(YAHOO.webtools.FeedsReader, YAHOO.widget.Module);

// Define global variables for the ajax requests
YAHOO.webtools.FeedsReader.TIMER = null;
YAHOO.webtools.FeedsReader.FEEDSERVER = "http://localhost:8030/RssReader/feedsServer";
YAHOO.webtools.FeedsReader.FREQUENCYRATE = 60000; //Time in milliseconds
YAHOO.webtools.FeedsReader.CALLBACKTIMEOUT = 20000;

// Structure layers definition
YAHOO.webtools.FeedsReader.numberSelectOptions = ''+
                                                '<option value="1">1</option>'+
                                                '<option value="5">5</option>'+
                                                '<option value="10">10</option>'+
                                                '<option value="15">15</option>'+
                                                '<option value="20">20</option>'+
                                                '<option value="30">30</option>'+
                                                '<option value="50">50</option>'+
                                                '';
YAHOO.webtools.FeedsReader.frequencySelectHour = ''+
                                                '<option value="0">00</option>'+
                                                '<option value="1">01</option>'+
                                                '<option value="2">02</option>'+
                                                '<option value="3">03</option>'+
                                                '<option value="4">04</option>'+
                                                '<option value="5">05</option>'+
                                                '';
YAHOO.webtools.FeedsReader.frequencySelectMinute = ''+
                                                //'<option value="0">00</option>'+
                                                '<option value="10">10</option>'+
                                                '<option value="20">20</option>'+
                                                '<option value="30">30</option>'+
                                                '<option value="40">40</option>'+
                                                '<option value="50">50</option>'+
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
                                        YAHOO.webtools.FeedsReader.numberSelectOptions+
                                        '</select> elements&nbsp;&nbsp;&nbsp;&nbsp;'+
                                        //'<select class="frWidgetFrequencySelect">'+
                                        //YAHOO.webtools.FeedsReader.frequencySelectHour+
                                        //'</select>&nbsp;:&nbsp;'+
                                        '<select class="frWidgetFrequencySelect">'+
                                        YAHOO.webtools.FeedsReader.frequencySelectMinute+
                                        '</select> refresh&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+
                                        '<input type="button" value="default" class="frWidgetDefaultSetup" />&nbsp;&nbsp;'+
                                        '<input type="button" value="close" class="frWidgetClose" />'+
                                        '</form>'+
                                        '</div>'+
                                        '';
YAHOO.webtools.FeedsReader.BODY_HTML = '';
YAHOO.webtools.FeedsReader.FOOTER_HTML = '';
                                                                                                                                                             
YAHOO.webtools.FeedsReader.OUTPUT_MODULE = null;


// Presentation layers definition
YAHOO.webtools.FeedsReader.CSS_FEEDSREADER = "frWidget";
YAHOO.webtools.FeedsReader.CSS_DASHBOARDWIDGET = "DashboardWidget";



// Global variable for ajax reponse handling
YAHOO.webtools.FeedsReader.AJAX_FEEDS_REQUEST = {
	handleSuccess: function (o)
	{
                
                if (o.responseXML)
		{
			var feeds = this.xmlParser(o.responseXML);
			var limit = this.root.cfg.getProperty('feedsNumber');
			this.setOutput(feeds,limit);
	
			if (this.userRequest)
			{
				if (this.root.cfg.getProperty("feedsNumber")!=this.params[0] && this.root.cfg.getProperty("feedsFrequency")==this.params[1]) {
					this.root.cfg.setProperty("feedsNumber",this.params[0]);
					}
				else if (this.root.cfg.getProperty("feedsNumber")==this.params[0] && this.root.cfg.getProperty("feedsFrequency")!=this.params[1]) {
					this.root.cfg.setProperty("feedsFrequency",this.params[1]);
					}
				else {
					this.root.cfg.setProperty("feedsNumber",this.params[0]);
					this.root.cfg.setProperty("feedsFrequency",this.params[1]);
					}
			}
		var delay = parseInt(o.argument.cfg.getProperty("feedsFrequency")) * YAHOO.webtools.FeedsReader.FREQUENCYRATE;
		if (o.argument.TIMER) clearTimeout(o.argument.TIMER);
		//o.argument.TIMER = setTimeout(function(thisObj) { thisObj.cfg.refireEvent('feedsURL'); }, delay, o.argument);
		o.argument.TIMER = setTimeout(function() { o.argument.cfg.refireEvent('feedsURL'); }, delay);
		}
		else 
		{	
      var p = '';
			var json = '';
			
			if (o.responseText.indexOf('feeds') >= 0) {
				
				var delay = parseInt(o.argument.cfg.getProperty("feedsFrequency")) * YAHOO.webtools.FeedsReader.FREQUENCYRATE;
				
                                if (o.argument.TIMER) clearTimeout(o.argument.TIMER);
                                //o.argument.TIMER = setTimeout(function(thisObj) { thisObj.cfg.refireEvent('feedsURL'); }, delay, o.argument);
				o.argument.TIMER = setTimeout(function() { o.argument.cfg.refireEvent('feedsURL'); }, delay);

				try {
					json = eval( '(' + o.responseText + ')' );
				}
				catch (e) {alert(o.responseText); return;}
				var f = json.feeds;
                                var feeds = new Array();                                                                                                                           
                        	for (var i=0; i<f.length; i++) {
					var feed = new Object();
                                        feed.title=f[i].title;
                                        feed.content=f[i].content;
                                        feed.updated=f[i].date+", "+f[i].time;
                                        feed.link=f[i].link;
                                        
					feeds.push(feed);
                                	}
				var limit = this.root.cfg.getProperty('feedsNumber');
                        	this.setOutput(feeds,limit);
				}
			else {
                        	p = o.responseText.split("=");
			
				if (!o.argument.cfg.getProperty("USER")){
					if (p[0]=="fn" && p[1]!=o.argument.cfg.getProperty("feedsNumber")) o.argument.cfg.setProperty("feedsNumber", p[1]);
                        		else if (p[0]=="fn" && p[1]==o.argument.cfg.getProperty("feedsNumber")) {
						if (!o.argument.cfg.getProperty('FLAG')) o.argument.cfg.setProperty("FLAG", true);
						else {
							o.argument.cfg.fireQueue();
							o.argument.cfg.setProperty("FLAG", false);
							o.argument.cfg.setProperty("USER",true);
							}
						}
 
					if (p[0]=="ff" && p[1]!=o.argument.cfg.getProperty("feedsFrequency")) o.argument.cfg.setProperty("feedsFrequency", p[1]);
					else if (p[0]=="ff" && p[1]==o.argument.cfg.getProperty("feedsFrequency")) {
                                		if (!o.argument.cfg.getProperty('FLAG')) o.argument.cfg.setProperty("FLAG", true);
                                		else {
							o.argument.cfg.fireQueue();
							o.argument.cfg.setProperty("FLAG", false);
							o.argument.cfg.setProperty("USER",true);
							}
						}
					}
				else {o.argument.cfg.refireEvent('feedsURL');}
				}
		}	
	},
	handleFailure: function (o)
	{
		alert("configuration request failed: "+o.statusText);	//o.getAllResponseHeaders
	
		if (this.userRequest)
		{
			if (this.root.cfg.getProperty("feedsNumber")!=this.params[0] && this.root.cfg.getProperty("feedsFrequency")==this.params[1])
			{
				var old_value = this.root.cfg.getProperty("feedsNumber");
				this.root.cfg.setProperty("feedsNumber",old_value);
			}
			else if (this.root.cfg.getProperty("feedsNumber")==this.params[0] && this.root.cfg.getProperty("feedsFrequency")!=this.params[1])
			{
				var old_value = this.root.cfg.getProperty("feedsFrequency");
				this.root.cfg.setProperty("feedsFrequency",old_value);
			}
			else
			{
				var old_value = this.root.cfg.getProperty("feedsNumber");
				this.root.cfg.setProperty("feedsNumber",old_value);
				
				old_value = this.root.cfg.getProperty("feedsFrequency");
				this.root.cfg.setProperty("feedsFrequency",old_value);
			}
		}
	},
	xmlParser: function (xml)
	{
		var feeds = new Array();
		var entries = '';
		var rss = false;
		var atom = false;
	   	
		if (xml.getElementsByTagName("item").length > 0) {
			rss = true;
			entries = xml.getElementsByTagName("item");
			}
		else if (xml.getElementsByTagName("entry").length > 0) {
				atom = true;
				entries = xml.getElementsByTagName("entry");
				}
 

		// Workaround to leverage the differences between safari and firefox.
      		/*
		var hack_getText =  function (element)
       		{
			var hack_hasInnerText = (document.getElementsByTagName("body")[0].innerText != undefined) ? true : false;

			if(!hack_hasInnerText)
        		{ 
          		 	return element.textContent;
           	 	}
			else
			{
               		 	return element.innerHTML;
         	  	 }
       		 }
		*/
		
		for(var i = 0; i < entries.length; i++) 
		{
			var entry = entries[i];
			var feed = new Object();
 	
			for (var j=0; j<entry.childNodes.length; j++) {
				if(atom) {
					if(entry.childNodes[j].nodeName=="title") {feed.title=entry.childNodes[j].firstChild.nodeValue;}
					if(entry.childNodes[j].nodeName=="content") {feed.content=entry.childNodes[j].getElementsByTagName("div")[0].innerHTML;}
					if(entry.childNodes[j].nodeName=="updated") {feed.updated=entry.childNodes[j].firstChild.nodeValue;}
					if(entry.childNodes[j].nodeName=="link") {feed.link=entry.childNodes[j].getAttribute("href");}
					}
				else if (rss) {
					if(entry.childNodes[j].nodeName=="title") {feed.title=entry.childNodes[j].firstChild.nodeValue;}
                                        if(entry.childNodes[j].nodeName=="description") {feed.content=entry.childNodes[j].getElementsByTagName("div")[0].innerHTML;}
                                        if(entry.childNodes[j].nodeName=="pubDate") {feed.updated=entry.childNodes[j].firstChild.nodeValue;}
                                        if(entry.childNodes[j].nodeName=="link") {feed.link=entry.childNodes[j].firstChild.nodeValue;}

					}
				}
				
			feeds.push(feed);
		}


		
		return feeds;
	},
	setOutput: function (feeds,limit)
	{
		
		var output = '';
		
		for(var i=0; i<feeds.length && i<limit; i++) {
			var output_tmp = '';

			output_tmp += "<div>"+"<img src='../RssReader/css/plus.png' alt='' title='read more' id=\'"+i+"\' class='feedimg' /> " + feeds[i].title;
			output_tmp += " <a href='" + feeds[i].link + "'><img src='css/external.png'/></a>";
			output_tmp += " <span class='rssdate'>[" + feeds[i].updated  + "]</span></div>";
			output_tmp += "<div id=\'content_"+i+"\' class='feedcontent'> " + feeds[i].content + "</div>";

			var pattern = /\S*/i;	// is not empty
			if(pattern.test(output_tmp)) {
				output +="<div class='feedcontainer'>"+output_tmp+"</div>";
				} 
			}
		

		var root = this.root.element;
		YAHOO.util.Dom.addClass(YAHOO.util.Dom.getElementsByClassName ("bd", "div", root)[0], "wrap");
		this.module.setBody(output);
		this.module.render(YAHOO.util.Dom.getElementsByClassName ("bd", "div", root)[0]);
				
		var imgs = YAHOO.util.Dom.getElementsByClassName ("feedimg", "img", root);
		
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
	root: null,
	params: null,
	userRequest: null
};




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

		this.cfg.setProperty("USER", false);

		//frWidgetSetUp Form INITIALIZATION EVENTS LISTENERS
		
		var frSetup = YAHOO.util.Dom.getElementsByClassName ("frWidgetSetup","div",root)[0];
		frSetupModule = new YAHOO.widget.Module(frSetup, { visible:false });
		frSetupModule.render();
		
		if(!this.cfg.getProperty("feedsNumber")) this.cfg.setProperty("feedsNumber",-1);
		if(!this.cfg.getProperty("feedsFrequency")) this.cfg.setProperty("feedsFrequency",-1);
	
		var frClose = YAHOO.util.Dom.getElementsByClassName ("frWidgetClose","input",root)[0];
		var frDefault = YAHOO.util.Dom.getElementsByClassName ("frWidgetDefaultSetup","input",root)[0];	
		var frToggle = YAHOO.util.Dom.getElementsByClassName ("frWidgetToggleSetup","img",root)[0];
		var frNumber = YAHOO.util.Dom.getElementsByClassName ("frWidgetNumberSelect","select",root)[0];
		var frFrequency = YAHOO.util.Dom.getElementsByClassName ("frWidgetFrequencySelect","select",root)[0];

		YAHOO.util.Event.addListener(frClose, "click", frSetupModule.hide, frSetupModule, true);
		YAHOO.util.Event.addListener(frDefault, "click", this.setupDefault, this, true);	
		YAHOO.util.Event.addListener(frToggle, "click", this.setupToggle, frSetupModule, true);
		YAHOO.util.Event.addListener(frNumber, "change", this.setupNumber, this, true);
		YAHOO.util.Event.addListener(frFrequency, "change", this.setupFrequency, this, true);

		// INITIALIZATION & GLOBAL VARIABELS SET UP 

		if(!this.cfg.getProperty("feedsURL")) this.cfg.queueProperty("feedsURL",YAHOO.webtools.FeedsReader.FEEDSERVER);
		
	        	
	}, this, true);
		
	this.initEvent.fire(YAHOO.webtools.FeedsReader);
	};


// Default config

YAHOO.webtools.FeedsReader.prototype.initDefaultConfig = function ()
{
	YAHOO.webtools.FeedsReader.superclass.initDefaultConfig.call (this);
   
	this.cfg.addProperty ("feedsNumber", {handler:this.configFeedsNumber, suppressEvent:true});
	this.cfg.addProperty ("feedsFrequency", {handler:this.configFeedsFrequency, suppressEvent:true}); 
	this.cfg.addProperty ("feedsURL", {handler:this.configFeedsRequest, suppressEvent: true});
	this.cfg.addProperty ("setupURL", {handler:this.configSetupRequest, suppressEvent: true});
	this.cfg.addProperty ("FLAG", {handler:'', suppressEvent: true});
	this.cfg.addProperty ("USER", {handler:'', suppressEvent: true});
        this.cfg.addProperty ("number", {handler:this.configNumberControl, suppressEvent: true});
        this.cfg.addProperty ("frequency", {handler:this.configFrequencyControl, suppressEvent: true});
};

YAHOO.webtools.FeedsReader.prototype.configNumberControl = function (type, args, obj)
{
}

YAHOO.webtools.FeedsReader.prototype.configFrequencyControl = function (type, args, obj)
{

}


YAHOO.webtools.FeedsReader.prototype.configFeedsRequest = function (type, args, obj)
{
	var feedsSourceURL = args[0];

	var ajaxRequest = YAHOO.webtools.FeedsReader.AJAX_FEEDS_REQUEST;
	
	var root = this.element;

	var parameters = '';
	
	/*
	if (document.getElementById(root.id+"_output")) {
		//alert("riga 276");
		var oldModule = document.removeNode(root.id+"_output");
		var parent = oldModule.parentNode;
		parent.removeChild(oldModule);
		}
	*/
	
	var frOutputModule = new YAHOO.widget.Module(root.id+"_output");
	ajaxRequest.module = frOutputModule;
	ajaxRequest.root = this;
		
	var callback = 
	{
		success: ajaxRequest.handleSuccess,
		failure: ajaxRequest.handleFailure,
		scope: ajaxRequest,
		argument: this,
		timeout: YAHOO.webtools.FeedsReader.CALLBACKTIMEOUT
	};
		
	var transaction = YAHOO.util.Connect.asyncRequest("GET",feedsSourceURL+parameters,callback, null);
   
};

YAHOO.webtools.FeedsReader.prototype.configSetupRequest = function (type, args, obj)
{
};

YAHOO.webtools.FeedsReader.prototype.configFeedsNumber = function (type, args, obj)
{
	var fn = args[0];

	var ajaxRequest = YAHOO.webtools.FeedsReader.AJAX_FEEDS_REQUEST;
	var url = YAHOO.webtools.FeedsReader.FEEDSERVER;
	var parameters = '';

        if (fn!=-1) {
		parameters = "?feedsNumber="+fn;		

		var i = args[0];
		var root = this.element;
		var selectControl = YAHOO.util.Dom.getElementsByClassName ("frWidgetNumberSelect","select",root)[0];
		var selectOptions = selectControl.getElementsByTagName("option");
		for (var k = 0; k<selectOptions.length; k++) {
			if (k == i-1) selectOptions[k].selected="selected"; //selectOptions[k].setAttribute("selected","selected");
			else if(selectOptions[k].selected) selectOptions[k].removeAttribute("selected");
			}
		}
	else {
        	parameters = "?feedsNumber=-1";
		}

	var callback =
	{
		success: ajaxRequest.handleSuccess,
		failure: ajaxRequest.handleFailure,
		scope: ajaxRequest,
		argument: this,
		timeout: YAHOO.webtools.FeedsReader.CALLBACKTIMEOUT
	};

	var transaction = YAHOO.util.Connect.asyncRequest("GET",url+parameters,callback, null);
	
	
};

YAHOO.webtools.FeedsReader.prototype.configFeedsFrequency = function (type, args, obj)
{
        var ajaxRequest = YAHOO.webtools.FeedsReader.AJAX_FEEDS_REQUEST;
        var url = YAHOO.webtools.FeedsReader.FEEDSERVER;

	var ff = args[0];
        
	if (ff!=-1) {
		parameters = "?feedsFrequency="+ff;		

		var i = args[0]+'';
		var root = this.element;
		var selectControl = YAHOO.util.Dom.getElementsByClassName ("frWidgetFrequencySelect","select",root)[0];
		var selectOptions = selectControl.getElementsByTagName("option");
		for (var k = 0; k<selectOptions.length; k++) {
			if (selectOptions[k].value == i) selectOptions[k].selected="selected";
			else if(selectOptions[k].selected) selectOptions[k].removeAttribute("selected");
			}
		}
	else {
                var parameters = "?feedsFrequency=-1";
		}

        var callback =
        {
                success: ajaxRequest.handleSuccess,
                failure: ajaxRequest.handleFailure,
                scope: ajaxRequest,
		argument: this,
                timeout: YAHOO.webtools.FeedsReader.CALLBACKTIMEOUT
        };
        
	var transaction = YAHOO.util.Connect.asyncRequest("GET",url+parameters,callback, null);

};



// My customized methods


// Managing and showing the parsed result

YAHOO.webtools.FeedsReader.prototype.setupDefault = function (e,obj)
{
	obj.cfg.setProperty("feedsNumber",5);
	obj.cfg.setProperty("feedsFrequency",10);
}

YAHOO.webtools.FeedsReader.prototype.setupToggle = function (e)
{
	if(frSetupModule.cfg.getProperty("visible")) frSetupModule.hide();
	else frSetupModule.show();
}


YAHOO.webtools.FeedsReader.prototype.setupNumber = function (e, obj) {
	var parameter = e.target.value;
	
	obj.cfg.setProperty("feedsNumber",parameter);
	}

YAHOO.webtools.FeedsReader.prototype.setupFrequency = function (e, obj) {
	var parameter = e.target.value;
	
	obj.cfg.setProperty("feedsFrequency",parameter);
	}


YAHOO.webtools.FeedsReader.prototype.test = function () { return '5'; }


