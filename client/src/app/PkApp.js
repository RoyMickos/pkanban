/**
 * @author Roy Mickos
 * 
 * This will be a standard, singleton javascript class and not a Dojo class, as this represents
 * the application and not a widget. 
 */
define.amd.jQuery = true;

define([
    "dijit/layout/BorderContainer", 
    "dijit/layout/ContentPane",
    "dijit/layout/TabContainer",
    "./PkPomodoro",
    "./PkModel",
    "jquery",
    "dojo/domReady!"
], function(BorderContainer, ContentPane, TabContainer, PkPomodoro, PkModel,$){
	return function() {
		this.taskId = 0;

		
		this.statusReport = function(data){
			for (elem in data) {
				console.log(elem + ": " + data[elem]);
			}
		};
		
		this.model = new PkModel(this.statusReport);
		
		this.recordProgress = function(minutes, seconds, isInterrupted){
			console.log("PkApp.recordProgress called with argument: " + minutes + ":" + seconds);
			if (!isInterrupted){
				$('#pomo_end').get(0).play();
			}
			if (this.taskId && minutes > 0) {
				this.model.recordProgress(this.taskId, minutes);
			};
		};
		
		this.startup = function(domElem){
			this.domElem = domElem;
			this.widgets = {};
			
			this.widgets.main = new BorderContainer({
				style: "width: 800px; height:500px;"
			});
			
			this.widgets.top = new ContentPane({
				region: "top"
			});
			this.widgets.main.addChild(this.widgets.top);
			
			this.widgets.left = new ContentPane({
				region: "left",
				content: "left",
				style: "width: 100px;"
			});
			this.widgets.pomodoro = new PkPomodoro({
				recordProgress: this.recordProgress, 
				style: "width: 100px;",
				id: "pkpomodoro"
			});
			this.widgets.left.addChild(this.widgets.pomodoro);
			this.widgets.main.addChild(this.widgets.left);
			
			this.widgets.center = new TabContainer({
				region: "center",
				tabPosition: "top",
				style: "width: 600px;"
			});
			this.widgets.main.addChild(this.widgets.center);
			
			/*
						this.pktabone = new ContentPane({
						title: "tabu 1",
						content: "tab 1"
					});
					this.pktabtwo = new ContentPane({
						title:   "tabu 2",
						content: "tab 2"
					});
			
			this.widgets.right = new ContentPane({
				region: "right",
				style: "width: 0px;"
			});
			this.widgets.main.addChild(this.widgets.right);
			*/
					
			this.widgets.bottom = new ContentPane({
				region: "bottom",
				content: "",
				id: 'pkmessage_area'
			});
			this.widgets.main.addChild(this.widgets.bottom);
			
			this.widgets.main.placeAt(this.domElem);
			this.widgets.main.startup();
			//this.widgets.main.show();
		};
	};
});
