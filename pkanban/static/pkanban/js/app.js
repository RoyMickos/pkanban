
var pkanbanApi = angular.module('pkanban.api',["ngResource","ngSanitize"]);

pkanbanApi.factory('Wip', ['$resource', function($resource) {
  return $resource('/pk/wip', {}, {
    query: {method: 'GET', params: {}, isArray:true}
  });
}]);

pkanbanApi.factory('Task', ['$resource', function($resource){
  return $resource('/pk/task/:id', {}, {
    query: {method: 'GET', params: {}, isArray:false},
    //get: {method: 'GET', params: {id: '@id'}},
    add_effort: {method: 'POST', params: {id: '@id'}}
  });
}]);

pkanbanApi.factory('Valuestream', ['$resource', function($resource) {
  return $resource('/pk/valuestream/:streamname', {}, {
    query: {method: 'GET', params: {}, isArray:true},
    set: {method: 'GET', params: {streamname: '@streamname'}}
  });
}]);


var pkanbanApp = angular.module('pkanbanApp',["ui.bootstrap", "pkanban.api"]);


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

pkanbanApp.directive('pkTaskEdit', function() {
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
      var ck = CKEDITOR.inline(elm[0]);

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


pkanbanApp.directive('pkMainView', function() {
  return {
    restrict: 'E',
    transclude: true,
    scope: {},
    controller: function($scope) {
      var panes = $scope.panes = [];

      $scope.select = function(pane) {
        angular.forEach(panes, function(pane) {
          pane.selected = false;
        });
        pane.selected = true;
      };

      this.addPane = function(pane) {
        if (panes.length === 0) {
          $scope.select(pane);
        }
        panes.push(pane);
      };

    },
    templateUrl: '/static/pkanban/templates/main-view.html'
  };
});

pkanbanApp.directive('pkTab', function(){
  return {
    require: '^pkMainView',
    restrict: 'E',
    transclude: true,
    scope: {
      title: '@'
    },
    link: function(scope, element, attrs, mainViewCtrl) {
      mainViewCtrl.addPane(scope);
    },
    templateUrl: '/static/pkanban/templates/tab-pane.html'
  };
});

pkanbanApp.controller('taskController', ['$scope', 'Task', function($scope, Task) {
  $scope.tasks = Task.query();
}]);
