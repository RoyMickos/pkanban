pkanbanApp.controller('wipController', ['$scope', 'Restangular',
   function($scope, Restangular) {

     var pkApi = Restangular.all('pk/');

     $scope.datamodel = {
       wip: [],
       wipData: [],
       valuestreams: [],
       current_task: undefined
     }
     $scope.unsavedChanges = false;
     $scope.currentTaskChanged = false;

     $scope.updateDatamodel = function () {
         $scope.datamodel.current_task = undefined;
         // get the base data
         pkApi.all('wip/').getList().then(function (wipList) {
           $scope.datamodel.wipData = wipList;
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
     //npm -> ../lib/node_modules/npm/bin/npm-cli.js
     $scope.findWipDataRecord = function(taskId){
       var wipData;
       //console.log(taskId);
       //console.log($scope.datamodel);
       for (i=0; i < $scope.datamodel.wipData.length; i++) {
         if (taskId === $scope.datamodel.wipData[i].task) {
           wipData = $scope.datamodel.wipData[i];
           break;
         }
       }
       return wipData;
     }

     $scope.findSituationData = function(task) {
       var record = $scope.findWipDataRecord(task.id);
       return record.situation;
     }

     $scope.updateSituationData = function(task, wipData){
       var retval = {
         past: [],
         present: undefined,
         future: []
       }, stream, numberOfStreams, phase, status = 'past';
       if ($scope.datamodel.valuestreams){
         numberOfStreams = $scope.datamodel.valuestreams.length;
       } else {
         numberOfStreams = 0;
       }
       //console.log($scope.datamodel.valuestreams);
       // find stream
       for (i=0; i < numberOfStreams; i++){
         //console.log($scope.datamodel.valuestreams[i].streamname + '/' + task.streamname);
         if ($scope.datamodel.valuestreams[i].streamname === task.valuestream) {
             stream = $scope.datamodel.valuestreams[i];
             break;
           }
       }
       // find phase
       phase = wipData.phase;

       // find past, present, and current phases
       if (stream && phase) {
         for(i=0; i < stream.phases.length; i++) {
           if (status === 'past') {
             if (stream.phases[i] === phase){
               retval.present = phase;
               status = 'future';
             } else {
               if (retval.past.length === 0) {
                 retval.past.push(stream.phases[i]);
               } else {
                 retval.past.push(stream.phases[i]);
               }
             }
           } else {
             retval.future.push(stream.phases[i]);
           }
         }
       }
       angular.extend(wipData, {situation: retval});
       return(retval);
     }

     $scope.getSituation = function(task) {
       var wipData;
       if (task) {
         wipData = $scope.findWipDataRecord(task.id);
       }

       if (wipData) {
         if (wipData.situation){
           return wipData.situation;
         } else {
           return $scope.updateSituationData(task, wipData);
         }
       }
     };

     $scope.set_current_task = function(task) {
       if ($scope.unsavedChanges){
         $scope.datamodel.current_task.put();
       }
       $scope.datamodel.current_task = task;
       $scope.currentTaskChanged = true;
     }

     $scope.saveCurrentTask = function() {
       if ($scope.datamodel.current_task){
         $scope.datamodel.current_task.put();
       }
     }

     $scope.advanceCurrentTask = function () {
       if ($scope.datamodel.current_task) {
         $scope.datamodel.current_task.doGET("advance_task/")
         .then(function () {
           $scope.updateDatamodel();
         }, function(response){
           console.log(response);
         });
       }
     }

     $scope.init = function() {
       console.log("Wip init called");
     };

     $scope.$watch("datamodel.current_task",
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
      situation: '=',
      advanceCurrentTask: '&',
      actionTooltip: '@'
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
          //scope.datamodel.current_task.$add_effort({},{minutes: minutes});
          if (minutes > 0){
            scope.datamodel.current_task.effort += minutes;
            scope.datamodel.current_task.put();
          }
          //scope.datamodel.current_task.customPOST({minutes: minutes},'add_effort/', {}, {});
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
      if (timerRunning) {
        stopTimer();
      } else {
        startTimer();
        pomodoroTimer = false;
      }
    });

    element.on('click', '.fa-circle-o-notch', function() {
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
