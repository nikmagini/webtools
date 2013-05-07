YAHOO.namespace("example.container");

function init() {					
	// Define various event handlers for Dialog
	var handleSubmit = function() {
		this.submit();
	};
	var handleCancel = function() {
		this.cancel();
	};
	//TODO: Put into one fuction
	var handleSuccess1 = function(o) {
		var response = o.responseText;
		response = response.split("<!")[0];
		document.getElementById("resp1").innerHTML = response;
		eval(response);
	};
	var handleSuccess2 = function(o) {
		var response = o.responseText;
		response = response.split("<!")[0];
		document.getElementById("resp2").innerHTML = response;
		eval(response);
	};
	var handleFailure = function(o) {
		alert("Submission failed: " + o.status);
	};
	//TODO: Put into one fuction
	// Instantiate the Dialogs
	YAHOO.example.container.dialog1 = new YAHOO.widget.Dialog("dialog1", 
																{ width : "500px",
																  fixedcenter : true,
																  visible : false, 
																  modal : true,
																  draggable: false,
																  close: false, 
																  iframe: true,
																  constraintoviewport : true,
																  buttons : [ { text:"Submit", handler:handleSubmit, isDefault:true },
																			  { text:"Cancel", handler:handleCancel } ]
																 } );
	
	YAHOO.example.container.dialog2 = new YAHOO.widget.Dialog("dialog2", 
																{ width : "600px",
																  fixedcenter : true,
																  visible : false, 
																  modal : true,
																  draggable: false,
																  close: false, 
																  iframe: true,
																  constraintoviewport : true,
																  buttons : [ { text:"Submit", handler:handleSubmit, isDefault:true },
																			  { text:"Cancel", handler:handleCancel } ]
																 } );
																 	
	// Wire up the success and failure handlers
	YAHOO.example.container.dialog1.callback = { success: handleSuccess1,
																 failure: handleFailure };
	
	YAHOO.example.container.dialog2.callback = { success: handleSuccess2,
																 failure: handleFailure };															 
					
	// Render the Dialogs
	YAHOO.example.container.dialog1.render();
	YAHOO.example.container.dialog2.render();
	
	YAHOO.util.Event.addListener("show1", "click", YAHOO.example.container.dialog1.show, YAHOO.example.container.dialog1, true);
	YAHOO.util.Event.addListener("show2", "click", YAHOO.example.container.dialog2.show, YAHOO.example.container.dialog2, true);
}

var handleSuccess3 = function(o){
	
	if(o.responseText !== undefined){
		var response = o.responseText;
		response = response.split("<!")[0];
		document.getElementById('software_container').innerHTML = response;
	}
}

var handleFailure = function(o){
	document.getElementById('software_container').innerHTML = "Request failed"
}

var callback =
{
  success:handleSuccess3,
  failure:handleFailure
};

function makeRequest(s){
	var sUrl = "/site/software?site="+s;
	var request = YAHOO.util.Connect.asyncRequest('GET', sUrl, callback);
}

YAHOO.util.Event.addListener(window, "load", init);