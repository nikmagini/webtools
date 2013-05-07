function insertFooter (page){
	var cssNode = document.createElement('link');
	cssNode.setAttribute('rel', 'stylesheet');
	cssNode.setAttribute('type', 'text/css');
	cssNode.setAttribute('href', '../../WEBTOOLS/Common/css/dmwt_footer_' + page + '.css');
	
	document.getElementsByTagName('head')[0].appendChild(cssNode); 

	YAHOO.namespace("cms.dmwt");
	YAHOO.cms.dmwt.footer = new YAHOO.widget.Overlay("footer", {  
																  visible:true,
																  width:"100%" } ); 
	YAHOO.cms.dmwt.footer.setBody(buildFooter(page));
	YAHOO.cms.dmwt.footer.cfg.setProperty("context", ["content", "tl", "tl"]); 
	
	YAHOO.cms.dmwt.footer.render(document.body); 
	YAHOO.cms.dmwt.footer.show();
}

function buildFooter(page){
	var text  = document.createElement ("p");
	changeText (text, "This is a footer");
	return text;
}