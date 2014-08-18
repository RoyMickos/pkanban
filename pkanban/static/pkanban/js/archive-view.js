/**
    achive view
*/
pkanbanApp.controller('archiveController', ['$scope', 'Restangular',
  function($scope, Restangular) {
    $scope.model = {
      tasks: []
    }

    var pkApi = Restangular.one('pk/');

    $scope.updateModel = function() {
      pkApi.getList('task',{filter: 'archive'})
      .then(function(archive){
        $scope.model.tasks = archive;
      }, function(err) {
        console.log("Error while retrieving archive:");
        console.log(err);
      });
    };

    $scope.saveChanges = function(task) {
      console.log("saveChanges called for task:");
      console.log(task);
    };

  }
]);

pkanbanApp.directive('pkArchiveTask', function() {
  return {
    restrict: 'E',
    scope: {
      task: '=',
      saveTask: '&'
    },
    templateUrl: '/static/pkanban/templates/archive-task.html'
  };
});

pkanbanApp.directive('pkArchiveHeader', function() {
  return {
    restrict: 'E',
    scope: {
      task: '='
    },
    templateUrl: '/static/pkanban/templates/archive-header.html'
  };
});
