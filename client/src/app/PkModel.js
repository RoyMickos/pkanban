/**
 * @author Roy Mickos
 * 
 * Represents back-end API for the controller
 * 
 */
define([
	"dojo/request/xhr",
	"dojo/on"
], function(request,on){
	return function (statusReport){
		
		// AJAX API for reporting progress for a task
		this.progressAddress= '/pkanban/effort/';
		this.recordProgress = function(taskId, minutes) {
			if (!taskId) return;
			submitData = {
				taskId: taskId,
				minutes: minutes
			};
			request.post(this.progressAddress, {
				data: submitData,
				headers: {"X-CSRFToken": csrftoken},
				handleAs: "json"
			}).then(function(data)
			{
				if (data.status == 'OK')
				{
					statusReport({
						message: "Pomodoro completed. Total effort now: " + data.effort + " minutes",
						effort: data.effort
					});
				} else
				{
					alert(data.msg);
				}
			}, function(err)
			{
				alert(err);
			});
		};	
	};
});
