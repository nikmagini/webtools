function cmsMain(){
	// Include the main css file
	var cssNode = document.createElement('link');
	cssNode.setAttribute('rel', 'stylesheet');
	cssNode.setAttribute('type', 'text/css');
	cssNode.setAttribute('href', '../css/dmwt_main.css');	
	document.getElementsByTagName('head')[0].appendChild(cssNode); 
	//Code for including stuff from http://ncyoung.com/entry/522
	/*
	var includes = getIncludes();
	for ( i = 0; i < includes.length; i++)	{
		var scriptNode = document.createElement('script');
		scriptNode.language='javascript';
		scriptNode.type='text/javascript';
		scriptNode.src='../masthead'; 
		document.getElementsByTagName("head")[0].appendChild(scriptNode);
	}	

	// Now we have scripts included we can add the masthead etc
	// Include the masthead
	insertMastHead ();*/
}

function getIncludes(){
	return 	[{file: "../../yui/build/yahoo/yahoo.js"},
	{file: "../../yui/build/dom/dom.js"},
	{file: "../../yui/build/event/event.js"},
	{file: "../../yui/build/container/container_core.js"},
	{file: "../masthead"}]
}