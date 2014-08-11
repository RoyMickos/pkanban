pkanbanApp.controller('wipController', ['$scope', '$sce', 'Wip', 'Valuestream',
   function($scope, $sce, Wip, Valuestream) {

     $scope.datamodel = {
       wip: Wip.query(),
       valuestreams: Valuestream.query(),
       current_task: undefined
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

     $scope.set_current_task = function(task) {
       $scope.datamodel.current_task = task;
     }

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
          console.log('Now reporting minutes back');
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
