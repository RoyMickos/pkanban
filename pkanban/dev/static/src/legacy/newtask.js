/* script code to check for correct form entry */

define.amd.jQuery = true;

require(["dojo/parser", 
         "dojo/request/xhr",
         "dijit/registry", 
         "dijit/Editor", 
         "dijit/form/TextBox",
         "dijit/form/Button", 
         "dijit/form/Select",
         "dojo/on", 
         "jquery",
         "pkutil",
         "dojo/_base/array",
         "dojo/domReady!"], 
function(parser, request, registry, Editor, TextBox, Button, Select, on, $, pkutil, array)
{
	parser.parse();
	/* debug: what have we parsed?
	console.log("Start of parsed elements:");
	array.forEach(registry.toArray(), function(item){
		console.log(item);
	});
	*/
	/*
	if (registry.byId('description_editor') === undefined)
	{
		console.log("We are screwed up already here");
	}
	*/
	var contentChanged = false;
	var messageboard = $("#message");
	var nametext = $("#name_input").val();
	var taskId = $('#task_id').text();
	var isCompleted = ($('#isCompleted').length > 0);
	var csrftoken = pkutil.getCookie('csrftoken');
	
	var idleInfo = function()
	{
		if (nametext.length == 0) {
			messageboard.text("Task name is mandatory")
		} else {
			messageboard.text("Last modified: " + $("#lastmodify").text())
		}		
	}
	
	// if taskId == 0 then this is a new task, so it has no description yet
	if (taskId != 0)
	{
		messageboard.text("Please wait, fetching description...")
		request.get('/pkanban/Description/' + taskId + '/', {
			handleAs: "text",
		}).then(function(data){
			var incomingData = pkutil.Base64.decode(data);
			registry.byId('description_editor').set("value",incomingData);
			//console.log(data);
			//console.log(incomingData);
			idleInfo();
		});
	} else
	{
		idleInfo();
	}
	
	// watch for changes
	var watchChanges = function()
	{
		contentChanged = true;
		console.log("Content changed");
	}
	on(registry.byId("description_editor"),'change', watchChanges);
	on(registry.byId("name_input"), 'change', watchChanges);
	
	var validateName = function() {
		var nametext = registry.byId("name_input").value;
		$("#message").text("validate name called, with name= " + nametext);
		if (nametext.length == 0) {
			// $("#name_errors").text("Task name is mandatory");
			alert("Task name is mandatory");
			$("#name_wrapper").css (errorHighlight );
			return false;
		}
		return true;
	};
	
	var valuestreamSelection = undefined;
	
	var createNewTask = function()
	{
		var submitData = {};
		if (validateName())
		{
			submitData.name = pkutil.Base64.encode(registry.byId("name_input").value);
			submitData.description = pkutil.Base64.encode(registry.byId("description_editor").value);
			var dbgOrig = registry.byId("description_editor").value;
			var dbgCoded = submitData.description;
			//return;
			if ($('#valuestream').length > 0)
			{
				submitData.valuestream = $('#valuestream_value').text();
			}
			else if ($('#vstream_select').length > 0)
			{
				//var vstream = registry.byId("vstream_select").value
				//var vstream = $(':selected').val();
				//console.log('valuestream: ' + valuestreamSelection);
				if (valuestreamSelection == " ")
				{
					valuestreamSelection = undefined;
				} else
				{
					submitData.valuestream = valuestreamSelection;
				}
			} else
			{
				console.log("Valuestream selection not in this page");
			}
			$('#message').text('Sending data to ' + location.pathname);
			request.post(location.pathname, {
				data: submitData,
				headers: {"X-CSRFToken": csrftoken},
				handleAs: "json",
			}).then(function(data)
			{
				if (data.status == 'OK')
				{
					location.assign(data.url);
					console.log(dbgOrig);
					console.log(dbgCoded);
				} else
				{
					alert(data.msg);
				}
			}, function(err)
			{
				alert(err);
			});
		}
	};
	
	var nextPhase = function()
	{
		$('#message').text('Sending request...');
		var csrftoken = pkutil.getCookie('csrftoken');
		var submitData = {
			taskid: taskId,
			forced: false
		};
		request.post('/pkanban/advance/', {
			data: submitData,
			headers: {"X-CSRFToken": csrftoken},
			handleAs: "json"
		}).then(function(data)
		{
			if (data.status == 'OK')
			{
				location.reload();
			} else
			{
				alert(data.msg);
			}
		}, function(err)
		{
			alert(err);
		});
	}
	
	var checkChangesBeforeLeaving = function()
	{
		if(contentChanged)
			if (!confirm("Content has been changed. Do you really want to leave without saving changes?"))
				return;
		location.assign('/pkanban/');
	}
	
	var deleteTask = function()
	{
		console.log('cancelTask called');
		var really = confirm("Do you really want to cancel this task?");
		if (really)
		{
			$('#message').text('Sending request...');
			var csrftoken = getCookie('csrftoken');
			var submitData = {
				taskid: taskId,
			};
			request.post('/pkanban/delete/', {
				data: submitData,
				headers: {"X-CSRFToken": csrftoken},
				handleAs: "json"
			}).then(function(data)
			{
				if (data.status == 'OK')
				{
					location.assign(data.url);
				} else
				{
					alert(data.msg);
				}
			}, function(err)
			{
				alert(err);
			});
		}
	}
	
	// Buttons ------------------------------------------------
	if (!isCompleted)
		on(registry.byId("submit_btn"), "click", createNewTask);
	
	if (!isCompleted && taskId > 0)
		on(registry.byId("delete_btn"), "click", deleteTask);
	
	on(registry.byId("cancel_btn"), "click", checkChangesBeforeLeaving);
	
	var select = registry.byId("vstream_select");
	if (select)
	{
		on(select, "change", function()
		{
			valuestreamSelection = this.value;
			$('#message').text("Remember to save your selection.")
		})
	}
	
	if (registry.byId("next_btn"))
	{
		on(registry.byId("next_btn"), "click", nextPhase)
	}
	
	// Pomodoro -----------------------------------------------
	var TimerActive = false;
	if (registry.byId("pomodoro"))
	{
		var pomoProgress = registry.byId("pomodoro");
		var interval = 1;  //timer tick in seconds
		var pomodoroTime = 25;
		pomoProgress.maximum = pomodoroTime * 60; // seconds in 25 minutes
		var timer = null;
		var mins = 25;
		var secs = 0;
		
		var setLabel = function()
		{
			if (secs < 10)
				pomoProgress.label = mins + ':0' + secs;
			else
				pomoProgress.label = mins + ':' + secs;			
		}

		setLabel();

		var recordProgress = function(minutes)
		{
			submitData = {
				taskId: taskId,
				minutes: minutes
			};
			request.post('/pkanban/effort/', {
				data: submitData,
				headers: {"X-CSRFToken": csrftoken},
				handleAs: "json"
			}).then(function(data)
			{
				if (data.status == 'OK')
				{
					$('#message').text("Pomodoro completed. Total effort now: " + data.effort + " minutes");
					$('#effort_value').text(data.effort);
				} else
				{
					alert(data.msg);
				}
			}, function(err)
			{
				alert(err);
			});
		}
		
		var pomoFunc = function()
		{
			pomoProgress.set("value", pomoProgress.value + 1);
			mins = Math.floor(pomoProgress.value / 60);
			secs = pomoProgress.value % 60;
			setLabel();
			if(pomoProgress.value > pomoProgress.maximum)
			{
				TimerActive = false;
				window.clearInterval(timer);
				$('#pomo_end').get(0).play();
				recordProgress(pomodoroTime);
			}
		}
		
		$('#pomo_wrapper').on('click', function(){
			if (TimerActive)
			{
				console.log("Timer is stopped");
				TimerActive = false;
				window.clearInterval(timer);
				console.log("value of timer: " + pomoProgress.value)
				recordProgress(Math.floor(pomoProgress.value/60))
			} else
			{
				console.log("Timer is started");
				TimerActive = true;
				pomoProgress.value = 0;
				timer = window.setInterval(function(){pomoFunc()}, interval*1000);
				$('#message').text("Running pomodoro...");
			}
			
		});
	}
});
	


