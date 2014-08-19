/**
    backlog view
*/
pkanbanApp.controller('backlogController', ['$scope', 'Restangular', 'NewTask',
  function($scope, Restangular, NewTask) {

  var pkApi = Restangular.one('pk/');

  $scope.model = {
    tasks: [],
    valuestreams: [],
    current_task: undefined,
    stream: undefined,
    error: undefined
  }
  $scope.unsavedChanges = false;
  $scope.currentTaskChanged = false;

  $scope.closeSemaphore = function() {
    NewTask.closeSemaphore();
  };

  $scope.updateModel = function() {
    $scope.model.current_task = undefined;
    $scope.model.stream = undefined;
    pkApi.getList('task',{filter: 'backlog'})
    .then(function(backlog){
      $scope.model.tasks = backlog;
    }, function(err) {
      console.log("Error while retrieving backlog:");
      console.log(err);
    });
    $scope.model.valuestreams = [];
    pkApi.getList('valuestream')
    .then(function(valuestreams){
      angular.forEach(valuestreams, function(value, index){
        $scope.model.valuestreams.push(value.streamname);
      });
    }, function(err) {
      console.log("Error while retrieving valuestreams");
      console.log(err);
    });
  };

  $scope.saveChanges = function(task) {
    if ($scope.model.current_task && $scope.unsavedChanges) {
      $scope.model.current_task.put();
    }
    $scope.model.current_task = task;
    $scope.model.stream = undefined;
    $scope.currentTaskChanged = true;
    $scope.unsavedChanges = false;
  };

  $scope.deleteTask = function(task) {
    task.remove()
    .then(function () {
      $scope.updateModel();
    }, function(err) {
      console.log("Removing task failed:");
      console.log("err");
    });
  };

  $scope.saveTask = function(task) {
    task.put();
  }

  $scope.$watch("model.current_task",
     function(newValue, oldValue) {
       if ($scope.currentTaskChanged){
         $scope.currentTaskChanged = false;
       } else {
         if(!angular.equals(newValue, oldValue))
           $scope.unsavedChanges = true;
       }
     },
     true
  );

  $scope.$watch(function() {
    return NewTask.taskSubmitSemaphore;
  },
    function(newValue, oldValue){
      if (newValue) {
        $scope.updateModel();
        $scope.closeSemaphore();
      }
    }
  );

  $scope.dismiss = function() {
    $scope.model.error = undefined;
  }

  $scope.selectValuestream = function(){
    if ($scope.model.current_task) {
      $scope.model.current_task.post('set_valuestream/', {valuestream: $scope.model.stream})
      .then(function() {
        $scope.updateModel();
      }, function(err){
        $scope.model.error = err.data + '  (' + err.status + ')';
      });
    }
    //$scope.model.error = "selecting valuestream " + $scope.model.stream + " for task " + $scope.model.current_task.name;
  };

}]);

pkanbanApp.directive('pkSelectValuestream', function() {
  return {
    restrict: 'E',
    scope: {
      streams: '=',
      task: '=',
      candidate: '=',
      select: '&',
      error: '=',
      errorAction: '&',
      deleteTask: '&',
      save: '&'
    },
    templateUrl: "/static/pkanban/templates/select-valuestream.html"
  };
});
