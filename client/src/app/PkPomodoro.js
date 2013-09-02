/**
 * @author Roy Mickos
 * 
 * TODO: we need to instantiate timer length from caller somehow, and have a default value here
 * maybe also a way of registering watchers for click events
 */
define.amd.jQuery = true;

define([
	"dojo/_base/declare",
	"dijit/ProgressBar",
	"dojo/_base/lang",
	"dojo/on",
	"jquery"
], function (declare, ProgressBar, lang, on, $) {
	return declare("pk.ProgressBar", ProgressBar, {
		tooltip: "Click to start/stop timer.",	
		
		constructor: function(args){
			declare.safeMixin(this, args);
			//if (this.pomoMins === undefined) declare.safeMixin(this, {pomoMins: 25});
			//if (this.pomoSecs === undefined) declare.safeMixin(this, {pomoSecs: 0});
			if (this.pomoMins === undefined) this.pomoMins = 25;
			if (this.pomoSecs === undefined) this.pomoSecs = 0;
		},
		
		postCreate: function() {
			declare.safeMixin(this, {
				_interval: 1,  //timer tick in seconds
				_timer: null,
				_mins: 0,
				_secs: 0,
				TimerActive: false,
				setLabel: function() {
					if (this._secs < 10)
						//this.label = this.mins + ':0' + this.secs;
						this.set("label", this._mins + ':0' + this._secs);
					else
						this.set("label", this._mins + ':' + this._secs);			
				},
				_onClick: function() {
					this.inherited(arguments);
				}
			}); // declare.safeMixin
			declare.safeMixin(this,{maximum: this.pomoMins * 60 + this.pomoSecs});
			
			var getPomoFunc = function(obj){
				 return function(){
					obj.set("value", (obj.get("value") + 1));
					obj._mins = Math.floor(obj.value / 60);
					obj._secs = obj.value % 60;
					obj.setLabel();
					if(obj.value >= obj.maximum)
					{
						obj.TimerActive = false;
						window.clearInterval(obj._timer);
						obj.recordProgress(obj.pomoMins, obj.pomoSecs, false);
					}			
				};
			};

/*			
			var getClickHandler = function(obj){
				return function(evt) {
					console.log("clicked!");
					if (obj.TimerActive)
					{
						console.log("Timer stopped");
						obj.TimerActive = false;
						window.clearInterval(obj.timer);
						console.log("value of timer: " + obj.value);
						obj.recordProgress(Math.floor(obj.value/60));
					} else
					{
						console.log("Timer started");
						obj.TimerActive = true;
						obj.value = 0;
						obj.timer = window.setInterval(getPomoFunc(obj), this.interval*1000);
					}
				};			
			};
*/
			
			var clickHandler = function() {
				console.log("Clicked!");
				if (this.TimerActive) {
					console.log("Timer stopped");
					this.TimerActive = false;
					window.clearInterval(this._timer);
					console.log("value of timer: " + this.value);
					this.recordProgress(Math.floor(this.value/60), this.value%60, true);
				} else
				{
					console.log("Timer started");
					this.TimerActive = true;
					this.value = 0;
					this._timer = window.setInterval(getPomoFunc(this), this._interval*1000);
				}
			};

			
			this.own(on(this.domNode,"click", lang.hitch(this, clickHandler)));
		},
		
		startup: function(){
			this.setLabel();
			//this.on("click", this.onClick);
		}
		
		//
	});
});
