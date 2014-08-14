/**
    backlog view
*/
pkanbanApp.controller('backlogController', ['$scope', 'Restangular',
  function($scope, Restangular) {

  var pkApi = Restangular.one('pk/');

  $scope.model = {
    tasks: [],
    current_task: undefined
  }
  $scope.unsavedChanges = false;
  $scope.currentTaskChanged = false;

  $scope.updateModel = function() {
    $scope.model.current_task = undefined;
    pkApi.getList('task',{filter: 'backlog'})
    .then(function(backlog){
      $scope.model.tasks = backlog;
    }, function(err) {
      console.log("Error while retrieving backlog:");
      console.log(err);
    });
  };

  $scope.saveChanges = function(task) {
    console.log("I was clicked!");
    console.log(task);
    if ($scope.model.current_task && $scope.unsavedChanges) {
      $scope.model.current_task.put();
    }
    $scope.model.current_task = task;
    $scope.currentTaskChanged = true;
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

}]);

pkanbanApp.directive('pkSelectValuestream', function() {
  return {
    restrict: 'E'
  };
});
