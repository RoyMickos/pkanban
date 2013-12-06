/**
 * @author Roy Mickos
 * 
 */

define.amd.jQuery = true;

require(["jquery", 
		 "pkutil",
		 "dijit/form/NumberSpinner", 
		 "dijit/form/TextBox", 
		 "dijit/form/SimpleTextarea", 
		 "dojo/on", 
         "dojo/request/xhr",
         "dijit/form/Button", 
         "dojo/parser",
         "dijit/registry",
         "dojo/domReady!"],
function($, pkutil, NumberSpinner, TextBox, SimpleTextarea, on, request, Button, parser, registry)
{
	parser.parse();
	on(registry.byId("cancel_btn"),'click',function() {
			location.assign('/pkanban/');
	});
	/**
	 * Phase handling
	 */
	var namebox = new TextBox({
		name: "Phase name",
		value: "",
		placeHolder: "Enter unique phase name"
	}, "pname");
	
	var capabox = new NumberSpinner({
		//name: "Phase capacity",
		value: 1,
		style: "width:3em",
		constraints: {min:1, max:10}
	}, "pcapa");
	
	var descbox = new SimpleTextarea({
		rows: 4,
		cols: 30
	}, "pdesc");
	
	// we need to grab the csrf token in order to communicate with the server
	var csrftoken = pkutil.getCookie('csrftoken');
	var checkName = function(aCategory, aName)
	{
		var verdict=true;
		$(aCategory).each(function(index)
		{
			if ($(this).text() == aName)
			{
				verdict=false;
			}
		});
		return verdict;
	};

	var sendAjaxData = function(url, senddata, emsg)
	{
		request.post(url, {
			data: senddata,
			headers: {"X-CSRFToken": csrftoken},
			handleAs: "json"
		}).then(function(data)
		{
			if (data.status == 'Error')
			{
				alert(emsg + ': ' + data.data);
			} else
			{
				$('#message').text('Waiting before reloading...');
				window.setTimeout(location.reload(), 2000);				
			}
		}, function(err)
		{
			alert(err);
		});
	};
	
	var newPhaseButton = new Button({
		iconClass:"dijitIconNewTask",
        showLabel:false,
        title: "Add new phase"
	}, 'npbutton');
	newPhaseButton.startup();
	
	on(newPhaseButton, "click", function(e){
		var newname = $("#pname").val();
		var capacity = $('#pcapa').val();
		var unique = checkName("td.pname", newname);
		if (! unique || newname.length == 0)
		{
			$('#message').text("Name is not unique or is empty");
			$("#pname_wrapper").css (errorHighlight);
		} else
		{
			var phasedata = {
				name: pkutil.Base64.encode(newname),
				capacity: capacity,
				description: pkutil.Base64.encode($('#pdesc').val())
			};
			sendAjaxData('/pkanban/nphase/', phasedata, "Adding phase failed");
		}
	}); //npbutton click event handler
	
	/**
	 * Valuestream handling
	 */
	
	var vstream_namebox = new TextBox({
		name: "Valuestream name",
		value: "",
		placeHolder: "Enter unique valuestream name"
	}, "vname");

	var newStreamButton = new Button({
		iconClass:"dijitIconNewTask",
        showLabel:false,
        title: "Start adding phases to valuestream"
	}, 'nvbutton');
	newStreamButton.startup();

	var checkPhases = function()
	{
		var phasename = $(this).text();
		var oldphases = $('#vphases').text();
		$(this).css ({'background-color':'#F0F0F0'});
		var selectedPhases = oldphases.split(',');
		$('#message').text(selectedPhases);
		// check that phase is not selected twice
		if (selectedPhases.indexOf(phasename) > -1)
		{
			$('#message').text('\"' + phasename + '\"" is already in this valuestream.');
		} else
		{
			$('#phases_wrapper').text($('#phases_wrapper').text() + phasename + ',');
		}
	}
	
	var valuestreamReady = function(e)
	{
		//$('#nvbutton').removeProp('disabled');
		//$('#cancelBtn').remove();
		var streamData = {
			//name: e.data.newname,
			name: pkutil.Base64.encode($('#vname').val()),
			phases: $('#phases_wrapper').text().replace(/[\n\t]/g,'')
		}
		console.log(streamData.phases);
		if (streamData.phases.length == 0)
		{
			$('#message').text("Please define at least one phase for the valuestream");
			$('#vphases').css(errorHighlight);
		} else 
		{
			sendAjaxData('/pkanban/nstream/', streamData, "Adding new valuestream failed");
		}
	}
	
	//on($("#nvbutton").get(0), "click", function(e)
	on(newStreamButton, "click", function(e)
	{
		var newname = $('#vname').val();
		var unique = checkName("td.vname", newname);
		if  (!unique || newname.length == 0 || (newname.indexOf(',') > -1))
		{
			$('#message').text("Name is not unique OR is empty OR contains a comma");
			$("#vname_wrapper").css (errorHighlight);
		} else
		{
			//$('#nvbutton').prop('disabled', true);
			newStreamButton.disabled = 'disabled';
			$('#button_wrapper').append('<input id="readyBtn" />');
			$('#button_wrapper').append('<input id="cancelBtn" />');
			var readyButton = new Button ({
				iconClass:"dijitIconSave",
        		showLabel:false,
        		title: "Done adding phases, commit changes."
			}, 'readyBtn');
			readyButton.startup();
			on(readyButton, "click", valuestreamReady);
			var cancelButton = new Button ({
				iconClass:"dijitIconClear",
				showLabel:false,
				title:"Cancel adding a valuestream."
			}, 'cancelBtn');
			cancelButton.startup();
			on(cancelButton, "click", function()
			{
				location.reload();
			});

			$('td.pname').on("click", checkPhases);
			$('#message').text("Select phases by clicking on their names");
			$('#backlog_wrapper').text('backlog,');
			$('#completed_wrapper').text('completed');
		}
	}); // nvbutton click event handler
});

