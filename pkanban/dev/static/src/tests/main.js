/*
 * This is the main test file. At the moment it is very simple and depends on the stucture of qunit-fixture
 */
define(['./pomotest', 'jquery', 'dojo/domReady!' ], function (pomotest, $) {
	
	// implement the test hook
	QUnit.jUnitReport = function(report) {
    	console.log(report.xml);
    	//TODO: upload to jenkins
	};

/*
	module("main tests");
	test( "a basic test example", function() {
	  var value = "hello";
	  equal( value, "hello", "We expect value to be hello" );
	});
*/
	pomotest();
	$testready = $('<div id="pkanban_testready"></div>');
	$testready.insertAfter("footer");

});