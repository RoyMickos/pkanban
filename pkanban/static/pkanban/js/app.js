
var pkanbanApp = angular.module('pkanbanApp',["ui.router", "ui.bootstrap", "restangular", "ngSanitize"]);

/**
  UI-Router configuration
*/

pkanbanApp.config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {

  $urlRouterProvider.otherwise('/wip');

  $stateProvider
  .state('wip', {
    url: '/wip',
    templateUrl: '/static/pkanban/templates/wip-tab.html',
    controller: 'wipController'
  })
  .state('backlog', {
    url: '/backlog',
    templateUrl: '/static/pkanban/templates/backlog-tab.html',
    controller: 'backlogController'
  })
  .state('done', {
    url: '/done',
    templateUrl: '/static/pkanban/templates/done-tab.html',
    controller: 'archiveController'
  });

}]);

/**
  Directives
*/

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
    this.taskSubmitSemaphore = false;
    this.openSemaphore = function() {
      this.taskSubmitSemaphore = true;
    };
    this.closeSemaphore = function () {
      this.taskSubmitSemaphore = false;
    };
  }
]);

pkanbanApp.controller('NewTaskCtrl', ['$scope', '$modal', '$log', 'Restangular', 'NewTask',
  function($scope, $modal, $log, Restangular, NewTask) {

    var pkApi = Restangular.one('pk/');

    $scope.new_task = NewTask.new_task;
    $scope.openSemaphore = function () {
      NewTask.openSemaphore();
    }
    //$scope.semaphore = NewTask.taskSumbitSemaphore;

    $scope.submit_task = function(){
      pkApi.post('task/', $scope.new_task)
      .then(function () {
        $scope.new_task.name = undefined;
        $scope.new_task.description = undefined;
        $scope.openSemaphore();
      }, function(err) {
        console.log("Error submitting new task:");
        console.log(err);
      });
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
