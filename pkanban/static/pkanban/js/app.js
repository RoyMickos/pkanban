
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
     $scope.datamodel = {
       wip: Wip.query(),
       valuestreams: Valuestream.query()
     }
     $scope.getStream = function(streamname) {
       var retval, streams = $scope.datamodel.valuestreams.length;
       for (i=0; i < streams; i++){
         if ($scope.datamodel.valuestreams[i].streamname === streamname) {
             retval = $scope.datamodel.valuestreams[i];
             break;
           }
         }
       return(retval);
     };
}]);

pkanbanApp.directive('pkTaskStreamBanner', ['Valuestream', function(Valuestream) {
  return {
    restrict: 'E',
    scope: {
      valuestream: '=',
      taskphase: '=',
    },
    templateUrl: '/static/pkanban/templates/task-stream-banner.html'
  };
}]);

pkanbanApp.directive('pkTaskView', function(Valuestream) {
  return {
    restrict: 'E',
    scope: {
      task: '=',
      mode: '=',
    },
    templateUrl: '/static/pkanban/templates/task-view.html'
  };
});

pkanbanApp.directive('pkTaskEdit', function(Valuestream) {
  return {
    restrict: 'E',
    scope: {
      task: '=',
      mode: '=',
    },
    templateUrl: '/static/pkanban/templates/task-edit.html'
  };
});

pkanbanApp.directive('ckEditor', function() {
  return {
    restrict: 'A',
    require: '?ngModel',
    link: function(scope, elm, attr, ngModel) {
      var ck = CKEDITOR.replace(elm[0]);

      if (!ngModel) return;

      // pasteState
      ck.on('change', function() {
        scope.$apply(function() {
          ngModel.$setViewValue(ck.getData());
        });
      });

      ngModel.$render = function(value) {
        ck.setData(ngModel.$viewValue);
      };
    }
  };
});


pkanbanApp.controller('taskController', ['$scope', 'Task', function($scope, Task) {
  $scope.tasks = Task.query();
}]);
