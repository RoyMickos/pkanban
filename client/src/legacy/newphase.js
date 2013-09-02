/**
 * @author Roy Mickos
 */
$(document).ready ( function()
	{
		var messageboard = $("#message");
		messageboard.text("Note: you can't change a phase once created!")
	});
	
var validateForm = function() {
	var name = $('#id_name').val();
	var capacity = $('#id_capacity').val();
}

var goBack = function() {
	window.history.back();
}
