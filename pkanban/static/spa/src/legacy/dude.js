// this is clip clap, half-finished code of ideas that did not work.


require([
    "dijit/layout/BorderContainer", 
    "dijit/layout/ContentPane",
    "dijit/layout/TabContainer",
    "dojo/domReady!"
], function(BorderContainer, ContentPane, TabContainer){
	var widgets = {};
	
	widgets.main = new BorderContainer({
		style: "width: 800px, height:500px"
	});
	
	widgets.top = new ContentPane({
		region: "top",
		content: "top pane"
	});
	widgets.main.addChild(widgets.top);
	
	widgets.left = 	new ContentPane({
		region: "left",
		content: "left",
		style: "width: 100px"
	});
	widgets.main.addChild(widgets.left);
	
	widgets.center = new TabContainer({
		region: "center",
		tabPosition: "top",
		style: "width: 600px"
	});
	widgets.main.addChild(widgets.center);
	
	/*
				this.pktabone = new ContentPane({
				title: "tabu 1",
				content: "tab 1"
			});
			this.pktabtwo = new ContentPane({
				title:   "tabu 2",
				content: "tab 2"
			});
	*/
	widgets.right = new ContentPane({
		region: "right",
		style: "width: 0px"
	});
			
			this.pkbottom = new ContentPane({
				region: "bottom",
				content: "message area"
			});
		},
		startup: function(){
			this.addChild(this.pktop);
			this.pktop.startup();
			
			this.pkleft = new ContentPane({
				region: "left",
				content: "left",
				style: "width: 100px"
			});
			this.addChild(this.pkleft);
			this.pkleft.startup();
			
			this.pkcenter.addChild(this.pktabone);
			this.pkcenter.addChild(this.pktabtwo);
			this.addChild(this.pkcenter);
			this.addChild(this.pkright);
			this.addChild(this.pkbottom);
		},
		show: function(){
			this.pktop.show();
			this.show();
		}
	});
});