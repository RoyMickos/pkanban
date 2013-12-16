/**
 * @author Roy Mickos
 */


var dojoConfig = {
    baseUrl: "../",
    async: true,
    isDebug: true,
    parseOnLoad: true,

    packages: [
        //dojo specific packages
        {name: "dojo", location: "static/js/src/dojo"},
        {name: "dijit", location: "static/js/src/dijit"},
        {name: "jquery", location: "static/js/src/jquery", main: "jquery-1.9.1.min"},
        {name: "pkutil", location: "static/js/src/app", main: "pkutil"}
    ],
    
    build: {
    	basePath: "..",
    	releaseDir: "../deploy",
    },

};
