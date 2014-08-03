
var pkanbanApi = angular.module('pkanban.api',["ngResource"]);

pkanbanApi.factory('Wip', ['$resource', function($resource) {
  return $resource('/pk/wip', {}, {
    query: {method: 'GET', params: {}, isArray:true}
  });
}]);

pkanbanApi.factory('Task', ['$resource', function($resource){
  return $resource('/pk/task/:id', {}, {
    query: {method: 'GET', params: {}, isArray:false}
  });
}]);

var pkanbanApp = angular.module('pkanbanApp',["ui.bootstrap", "pkanban.api"]);

pkanbanApp.controller('wipController', ['$scope', 'Wip', function($scope, Wip) {
  $scope.wip = Wip.query();
}]);

pkanbanApp.controller('taskController', ['$scope', 'Task', function($scope, Task) {
  $scope.tasks = Task.query();
}]);
