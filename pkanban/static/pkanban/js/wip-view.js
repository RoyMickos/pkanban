pkanbanApp.controller('wipController', ['$scope', 'Restangular',
   function($scope, Restangular) {

     var pkApi = Restangular.all('pk/');

     $scope.datamodel = {
       wip: [],
       valuestreams: [],
       current_task: undefined
     }

     $scope.updateDatamodel = function () {
         // get the base data
         pkApi.all('wip/').getList().then(function (wipList) {
           $scope.datamodel.wip = [];
           var items = wipList.length, wipItem;
           for (var i=0; i < items; i++) {
             wipItem = wipList[i];
             pkApi.one('task', wipItem.task).get().then(function (task) {
               $scope.datamodel.wip.push(task);
             }, function() {
               console.log('Error retrieving task id ' + wipItem.task);
             })
           }
         }, function errorCallback() {
           console.log('Error while retrieving WIP');
         });

         pkApi.all('valuestream/').getList().then(function (valuestreamList) {
           $scope.datamodel.valuestreams = valuestreamList;
         }, function errorCallback() {
           console.log('Error while retrieving valuestreams');
         });
     }

     $scope.getStream = function(streamname) {
       var retval, streams;
       if ($scope.datamodel.valuestreams){
        streams = $scope.datamodel.valuestreams.length;
      } else {
        streams = 0;
      }
       for (i=0; i < streams; i++){
         if ($scope.datamodel.valuestreams[i].streamname === streamname) {
             retval = $scope.datamodel.valuestreams[i];
             break;
           }
         }
       return(retval);
     };

     $scope.set_current_task = function(task) {
       //pkApi.one('task', taskId).get().then(function (task){
       $scope.datamodel.current_task = task;
       /*
       }, function errorCallback() {
         console.log("Error while retrieving task " + taskId);
       });
       //$scope.datamodel.current_task = Task.get({id: taskId});
       */
     }

     $scope.init = function() {
       console.log("Wip init called");
     };

     //$scope.updateDatamodel();

}]);

pkanbanApp.directive('pkTaskSelector', function() {
  function link(scope, element, attrs) {
    element.on('click', function(e) {
      e.preventDefault();

      scope.$apply(function() {
        scope.set_current_task({taskId: scope.task.id});
      });
    });
  };

  return {
    restrict: 'A',
    link: link,
    scope: {
      task: '=',
      set_current_task: '&onClick'
    }
  }
});

pkanbanApp.directive('pkTaskStreamBanner', function() {
  return {
    restrict: 'E',
    scope: {
      valuestream: '=',
      taskphase: '=',
    },
    templateUrl: '/static/pkanban/templates/task-stream-banner.html'
  };
});

pkanbanApp.directive('pkPomodoroTimer', ['$interval', function($interval) {

  function link(scope, element, attrs) {
    var timer, timerRunning=false, pomodoroTimer=true;
    scope.seconds = 0;
    scope.pomodoroTooltip = 'Click me for a 25 minute pomodoro.';
    scope.straightTimeTooltip = 'Click me for uninterrupted timing.';

    var updateTime = function() {
      scope.seconds += 1;
      if (pomodoroTimer && scope.seconds >= 1500){
        stopTimer();
        timerExpiredAlert();
      }
    }

    var timerExpiredAlert = function() {
      document.getElementById('timer-expired-alert').play();
    }

    var stopTimer = function() {
        $interval.cancel(timer);
        timerRunning = false;
        if(scope.datamodel.current_task) {
          var minutes = Math.round(scope.seconds/60);
          console.log('Now reporting ' + minutes + ' minutes back for task ' + scope.datamodel.current_task);
          //scope.datamodel.current_task.$add_effort({},{minutes: minutes});
          if (minutes > 0){
            scope.datamodel.current_task.effort += minutes;
            scope.datamodel.current_task.put();
          } else {
            console.log('Nothing to update');
          }
          //scope.datamodel.current_task.customPOST({minutes: minutes},'add_effort/', {}, {});
        } else {
          console.log(scope.datamodel);
        }
    }

    var startTimer = function() {
      scope.seconds = 0;
      timer = $interval(function() {
        updateTime();
      }, 1000);
      timerRunning = true;
    }

    element.on('$destroy', function() {
      $interval.cancel(timer);
    });

    // requires jquery, does not work with jqLite
    element.on('click', '.fa-clock-o', function() {
      console.log('straight timer started on:' + scope.datamodel.current_task);
      if (timerRunning) {
        stopTimer();
      } else {
        startTimer();
        pomodoroTimer = false;
      }
    });

    element.on('click', '.fa-circle-o-notch', function() {
      console.log('pomodoro started on' + scope.datamodel.current_task);
      if (timerRunning){
        stopTimer();
      } else {
        startTimer();
        pomodoroTimer = true;
      }
    })
  }

  return {
      restrict: 'E',
      link: link,
      templateUrl: '/static/pkanban/templates/task-timer.html'
    };

}]);

pkanbanApp.filter('timer', function() {
  return function(input){
    input = input || 0;
    var out = "";
    var minutes = Math.floor(input / 60);
    var seconds = input % 60;
    if (minutes < 10){
      out = '0'+minutes;
    } else {
      out = ''+minutes;
    }
    if (seconds < 10){
      out = out + ':0' + seconds;
    } else {
      out = out + ':' + seconds;
    }
    return out;
  };
});
