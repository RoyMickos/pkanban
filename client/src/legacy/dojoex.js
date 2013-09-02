// In demo/myModule.js (which means this code defines
// the "demo/myModule" module):
 
define([
    // Not using dojo/dom, instead using jQuery
    "dojo/fx","dojo/domReady!"
], function(fx){
    // Once all modules in the dependency list have loaded, this
    // function is called to define the demo/myModule module.
    //
    // The dojo/dom module is passed as the first argument to this
    // function; additional modules in the dependency list would be
    // passed in as subsequent arguments.
 
    var oldText = {};
 
    // This returned object becomes the defined value of this module
    return {
        setText: function(id, text){
            var node = $('#' + id);
            oldText[id] = node.text();
            node.text(text);
            fx.slideTo({
                top: 0,
                left: 5,
                node: greeting
            }).play();
        },
        restoreText: function(id){
            var node = $('#'+id);
            node.text(oldText[id]);
            delete oldText[id];
        }
    };
});