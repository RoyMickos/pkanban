/**
    backlog view
*/
pkanbanApp.controller('backlogController', ['$scope', 'Restangular',
  function($scope, Restangular) {

  var pkApi = Restangular.one('pk/');

  $scope.model = {
    tasks: [],
    valuestreams: [],
    current_task: undefined,
    stream: undefined
  }
  $scope.unsavedChanges = false;
  $scope.currentTaskChanged = false;

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

  /*
  $scope.$watch("model.stream",
    function(newValue, oldValue) {
      if (newValue === oldValue) {
        return
      } else {
        selectValuestream();
      }
    }
  )
  */

  $scope.selectValuestream = function(){
    /**
      This gets called by ng-change BEFORE the actual model change happens,
      so we need to defer the processing of the selection.
    */
    console.log("selecting valuestream " + $scope.model.stream + " for task " + $scope.model.current_task.name);
  };

}]);

pkanbanApp.directive('pkSelectValuestream', function() {
  return {
    restrict: 'E',
    scope: {
      streams: '=',
      task: '=',
      candidate: '=',
      select: '&'
    },
    templateUrl: "/static/pkanban/templates/select-valuestream.html"
  };
});
