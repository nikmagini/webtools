/*
//
// Question objects should contain the following
//
<fieldset id="q1" class="inline questionpane">
			<legend>Question 1.</legend>
			<center>
				<fieldset class="smallpanes inline">
					<legend>Question text</legend>
					<p>
						<textarea rows="3" cols="33"></textarea> 
					</p>
				</fieldset>
				<p></p>
				<fieldset class="smallpanes inline">
					<legend>Who to survey</legend>
					<!-- These values should come from the roles table in the DB -->
					<p><input type="checkbox" name="admins" value="1"/> - Site Administrator<br/>
					<input type="checkbox" name="managers" value="2"/> - Site Manager<br/>
					<input type="checkbox" name="datamanagers" value="3"/> - Data Manager<br/>
					<input type="checkbox" name="all" value="100"/> - All<br/><br/><br/></p>
				</fieldset>
				<fieldset class="smallpanes inline">
					<legend>Which sites to survey</legend>
					<!-- These values should come from the tiers table in the DB -->
					<p><input type="checkbox" name="t0" value="1"/> - Tier 0<br/>
					<input type="checkbox" name="t1" value="2"/> - Tier 1<br/>
					<input type="checkbox" name="t2" value="3"/> - Tier 2<br/>
					<input type="checkbox" name="t3" value="4"/> - Tier 3<br/>
					<input type="checkbox" name="tx" value="5"/> - Tier X/Opportunistic<br/>
					<input type="checkbox" name="all" value="100"/> - All</p>
				</fieldset>
				<p></p>
				<fieldset class="smallpanes inline">
					<legend>Closing Date</legend>
					<!-- Do this with the YUI calendar widget -->
					<p>
						<input type="text" name="date" size="10" maxlength="8" value="DD/MM/YY"/>
					</p>
				</fieldset>
				<fieldset class="smallpanes inline">
					<legend>Add/Remove Question</legend>
					<p class="small">
					<input type="button" value="Add Question"/>&nbsp;
					<input type="button" value="Remove Question"/><br/>
					<br/>Clicking add creates a new question</p>
				</fieldset>
			</center>
		</fieldset>
		<br/>
		<br/>
*/
document.writeln('<fieldset id="q1" class="inline questionpane">\n			<legend>Question 1.<\/legend>\n			<center>\n				<fieldset class="smallpanes inline">\n					<legend>Question text<\/legend>\n					<p>\n						<textarea rows="3" cols="33"><\/textarea> \n					<\/p>\n				<\/fieldset>\n				<p><\/p>\n				<fieldset class="smallpanes inline">\n					<legend>Who to survey<\/legend>\n					<!-- These values should come from the roles table in the DB -->\n					<p><input type="checkbox" name="admins" value="1"\/> - Site Administrator<br\/>\n					<input type="checkbox" name="managers" value="2"\/> - Site Manager<br\/>\n					<input type="checkbox" name="datamanagers" value="3"\/> - Data Manager<br\/>\n					<input type="checkbox" name="all" value="100"\/> - All<br\/><br\/><br\/><\/p>\n				<\/fieldset>\n				<fieldset class="smallpanes inline">\n					<legend>Which sites to survey<\/legend>\n					<!-- These values should come from the tiers table in the DB -->\n					<p><input type="checkbox" name="t0" value="1"\/> - Tier 0<br\/>\n					<input type="checkbox" name="t1" value="2"\/> - Tier 1<br\/>\n					<input type="checkbox" name="t2" value="3"\/> - Tier 2<br\/>\n					<input type="checkbox" name="t3" value="4"\/> - Tier 3<br\/>\n					<input type="checkbox" name="tx" value="5"\/> - Tier X\/Opportunistic<br\/>\n					<input type="checkbox" name="all" value="100"\/> - All<\/p>\n				<\/fieldset>\n				<p><\/p>\n				<fieldset class="smallpanes inline">\n					<legend>Closing Date<\/legend>\n					<!-- Do this with the YUI calendar widget -->\n					<p>\n						<input type="text" name="date" size="10" maxlength="8" value="DD\/MM\/YY"\/>\n					<\/p>\n				<\/fieldset>\n				<fieldset class="smallpanes inline">\n					<legend>Add\/Remove Question<\/legend>\n					<p class="small">\n					<input type="button" value="Add Question"\/>&nbsp;\n					<input type="button" value="Remove Question"\/><br\/>\n					<br\/>Clicking add creates a new question<\/p>\n				<\/fieldset>\n			<\/center>\n		<\/fieldset>\n		<br\/>\n		<br\/>');