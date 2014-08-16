// ngResource
//var pkanbanApi = angular.module('pkanban.api',["restangular","ngSanitize"]);

/*
pkanbanApi.config(['$resourceProvider', function($resourceProvider) {
  $resourceProvider.defaults.stripTrailingSlashes = false;
}]);
*/

/*
pkanbanApi.factory('Wip', ['$resource', function($resource) {
  return $resource('/pk/wip', {}, {
    query: {method: 'GET', params: {}, isArray:true}
  }, {stripTrailingSlashes: false});
}]);

pkanbanApi.factory('Task', ['$resource', function($resource){
  return $resource('/pk/task/:id/:action/', {}, {
    query: {method: 'GET', params: {}, isArray:false},
    get: {method: 'GET', params: {id: '@id'}},
    add_effort: {method: 'POST', params: {id: '@id', action: 'add_effort'}}
  }, {stripTrailingSlashes: false});
}]);

pkanbanApi.factory('Valuestream', ['$resource', function($resource) {
  return $resource('/pk/valuestream/:streamname', {}, {
    query: {method: 'GET', params: {}, isArray:true},
    set: {method: 'GET', params: {streamname: '@streamname'}}
  }, {stripTrailingSlashes: false});
}]);
*/

var pkanbanApp = angular.module('pkanbanApp',["ui.bootstrap", "restangular", "ngSanitize"]);


pkanbanApp.directive('pkTaskView', function() {
  return {
    restrict: 'E',
    scope: {
      task: '=',
      //selected: true
    },
    templateUrl: '/static/pkanban/templates/task-view.html'
  };
});

pkanbanApp.directive('pkTaskEdit', function() {

  /* in case task get changed, update content to reflect it
  function link(scope, element, attrs){
    console.log(attrs);
    scope.$watch(attrs.task, function(value) {
      console.log('task was changed: ' + value);
      scope.task = value;
    })
  }
  */

  return {
    restrict: 'E',
    scope: {
      task: '='
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

      var updateModel = function() {
        scope.$apply(function() {
          ngModel.$setViewValue(ck.getData());
        });
      };

      /* pasteState*/
      ck.on('change', updateModel);

      ngModel.$render = function(value) {
        // we use $apply() to update the content of ckeditor. but we need to
        // detach the updateModel function while doing so, since it would create
        // a nested call to $apply
        ck.removeListener('change', updateModel);
        ck.setData(ngModel.$viewValue);
        ck.on('change', updateModel);
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
        pane.init();
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
      title: '@',
      init: '&'
    },
    link: function(scope, element, attrs, mainViewCtrl) {
      mainViewCtrl.addPane(scope);
    },
    templateUrl: '/static/pkanban/templates/tab-pane.html'
  };
});

pkanbanApp.controller('taskController', ['$scope', 'Restangular', function($scope, Restangular) {
  var pkApi = Restangular.all('pk/');
  pkApi.all('task/').getList().then(function(tasks){
    $scope.tasks = tasks;
  }, function errorCallback() {
    console.log('Error while retrieving /pk/task list');
  });
  //$scope.tasks = Task.query();
}]);

// controller for the button to open new task modal
pkanbanApp.service('NewTask', ['$rootScope',
  function($rootScope) {
    this.new_task = {
      name: undefined,
      description: undefined,
      effort: 0
    };
  }
]);

pkanbanApp.controller('NewTaskCtrl', ['$scope', '$modal', '$log', 'Restangular', 'NewTask',
  function($scope, $modal, $log, Restangular, NewTask) {
    $scope.new_task = NewTask.new_task;

    $scope.submit_task = function(){
      console.log('Submit task called for:');
      console.log($scope.new_task);
      $scope.new_task.name = undefined;
      $scope.new_task.description = undefined;
    };

    $scope.open = function(){
      var modalInstance = $modal.open({
        templateUrl: '/static/pkanban/templates/new-task.html',
        controller: 'ModalInstanceCtrl',
        size: 'lg',
      });

      modalInstance.result.then(function (new_task) {
        $scope.new_task = new_task;
        $scope.submit_task();
      }, function() {
        $log.info('Cancelled new task creation');
      });
    };


}]);

// controller for the modal itself
pkanbanApp.controller('ModalInstanceCtrl', ['$scope', '$modalInstance', 'NewTask',
  function($scope, $modalInstance, NewTask){
    $scope.new_task = NewTask.new_task;

    $scope.create_task = function() {
      $modalInstance.close($scope.new_task);
    };

    $scope.cancel = function() {
      $modalInstance.dismiss('cancel');
    };
  }
]);
