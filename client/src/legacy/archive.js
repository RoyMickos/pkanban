/**
 * @author Roy Mickos
 */
require(['dijit/registry', 'dojo/parser', 'dojo/on', 'dijit/form/Button', 'dojo/domReady!'], 
	function(registry, parser, on)
	{
		parser.parse();
		on(registry.byId("cancel_btn"),'click',function() {
			location.assign('/pkanban/');
		})
	});