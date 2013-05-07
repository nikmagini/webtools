#!/usr/bin/env python

templateDef="""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
<!--Error handler--> 
 
<html xmlns="http://www.w3.org/1999/xhtml"> 
<head> 
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> 
        <title>CMS webtools error handler</title> 

        <link rel="stylesheet" type="text/css" href="/base/Common/mastheadcss?site=help"/> 
        
        <script type="text/javascript" src="/base/YUI/yui/js/?script=yahoo.js&script=dom.js&script=event.js&script=container_core.js&script=connection.js&script=dragdrop.js&script=container.js"></script> 
        <script type="text/javascript" src="/base/Common/masthead"></script> 
<script type="text/javascript">
function footerMenuText(){
    return [
{label: "Bug report", link: "https://savannah.cern.ch/bugs/?func=additem&group=webtools&custom_sb4=101&category_id=107", title: "Savannah bug report page for WEBTOOLS"}
    ]
}
</script>

</head> 
<body onload="insertMastHead ('help', '');" id="content"> 
<div>
<!-- 500 Internal Server Error -->
<h4>Unanticipated error</h4>
<p>
The server encountered an unexpected condition which prevented it from fulfilling the request.
</p>
</div>

<div> 
<h4>Report a bug</h4> 
<pre>
$msg
</pre>
<p>
We use the LCG savannah tool for bug tracking. 
<br/>
Please enter a bug via our project page 
<a href="https://savannah.cern.ch/bugs/?func=additem&group=webtools&custom_sb4=101&category_id=$systemId">here</a>. 
<br/>
Please report as much detail as possible. 
</p> 
</div> 

</body>
</html>
"""
