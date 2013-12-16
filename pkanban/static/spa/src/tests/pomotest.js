/**
 * @author Roy Mickos
 */
define.amd.jQuery = true;

define(['../app/PkPomodoro', 'jquery', 'dojo/domReady!'], function(PkPomodoro, $){
	return function(){
		// first we need to set up the fixture
		var hasReported = false;
		var wasInterrupted = false;
		var fixture = $("#qunit-fixture");
		var pomo = null;
		var recordProgress = function(minutes, seconds, isInterrupted){
				hasReported = true;
				wasInterrupted = isInterrupted;
		};
				
		module("pomodoro test 1",{
			setup: function(){
				hasReported = false
				if((fixture != null || fixture != undefined)){
					pomo = new PkPomodoro({
						recordProgress: recordProgress, 
						pomoMins: 0,
						pomoSecs: 10,
						style: "width: 100px;",
						id: "pkpomodoro"
					});
					pomo.placeAt(fixture[0]); // unwrap jquery object
					pomo.startup();
				} else {
					throw "Fixture not found!";
				}
			},
			teardown: function() {
				pomo.destroy();
				pomo = null;
			}
		});
		asyncTest("test pomodoro start-stop",
			function(){
				expect(4);
				console.log("reading label from widget instance: \"" + pomo.label + "\"");
				console.log("reading label through jquery:\"" + $("#pkpomodoro").text()+"\"");
				ok(($("#pkpomodoro") !== null), "testing existence");
				$("#pkpomodoro").trigger("click");
				// wait a couple of seconds to see that counter works. trouble is we can't wait
				window.setTimeout(function() {
									ok(($.trim($("#pkpomodoro").text()) > '0:00'));
									$("#pkpomodoro").trigger("click");
									equal(pomo.get("value"),2,"timer counted 2 seconds");
									ok(wasInterrupted, "timer expiration due to interrupt");
									start();
								  },
								  2500);
			}
		);
		asyncTest("test timer expiration",
			function() {
				expect(2);
				$("#pkpomodoro").trigger("click");
				pomo.set("value", pomo.get("maximum") - 2);
				window.setTimeout(function() {
					ok(hasReported);
					ok(!wasInterrupted);
					start();
				},
				2500);
			}
		);


		module("pomodoro test 2");
		test("test setting default value",
			function() {
				var pomo2 = new PkPomodoro();
				equal(25*60, pomo2.get("maximum"));
			});

	}; // return value function of define
	
});
