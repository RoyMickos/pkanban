
var pkanbanApi = angular.module('pkanban.api',["ngResource","ngSanitize"]);

pkanbanApi.factory('Wip', ['$resource', function($resource) {
  return $resource('/pk/wip', {}, {
    query: {method: 'GET', params: {}, isArray:true}
  });
}]);

pkanbanApi.factory('Task', ['$resource', function($resource){
  return $resource('/pk/task/:id', {}, {
    query: {method: 'GET', params: {}, isArray:false},
    get: {method: 'GET', params: {id: '@id'}}
  });
}]);

pkanbanApi.factory('Valuestream', ['$resource', function($resource) {
  return $resource('/pk/valuestream/:streamname', {}, {
    query: {method: 'GET', params: {}, isArray:true},
    set: {method: 'GET', params: {streamname: '@streamname'}}
  });
}]);

var pkanbanApp = angular.module('pkanbanApp',["ui.bootstrap", "pkanban.api"]);


pkanbanApp.controller('wipController', ['$scope', '$sce', 'Wip', 'Valuestream',
   function($scope, $sce, Wip, Valuestream) {
     $scope.wip = Wip.query();
     $scope.valuestreams = Valuestream.query();
     $scope.getPhases = function(stream) {
       var retval, streams = $scope.valuestreams.length;
       for (i=0; i < streams; i++){
         if ($scope.valuestreams[i].streamname === stream) {
             retval = $scope.valuestreams[i].phases;
             break;
           }
         }
       return(retval);
     };
}]);

pkanbanApp.controller('taskController', ['$scope', 'Task', function($scope, Task) {
  $scope.tasks = Task.query();
}]);