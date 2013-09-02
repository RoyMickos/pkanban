/* script utilities for the main page 
dojoConfig = {
	async: true,
	// This code registers the correct location of the "demo" package
	// so we can load Dojo from the CDN whilst still being able to
	// load local modules
	baseurl: "static/js/src/app",
	paths: {
		jquery: "app/jquery.js",
	}
};
*/
//'<table><thead><tr><th>Phase</th><th>Task</th><th>Valuestream</th></tr></thead></table>'
define.amd.jQuery = true;
require(["jquery","dojo/domReady!"], 
	function($)
{
	$("#board").load("wip");
	$("#backlog").load("backlog");
});
/*
	var csrftoken = getCookie('csrftoken');
	request('/pkanban/wip/', {
		handleAs: 'json','
		headers: {"X-CSRFToken": csrftoken},
	}).then(function(response){
		if (response.records == 0)
		{
			$('#board').html('<p class="remark">o work-in-progress tasks. Please select from backlog.</p>');
		} else
		{
			var aTable = $('<tbody></tbody>')
		}
	});
	
});
*/