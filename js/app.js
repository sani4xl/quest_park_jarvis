var app = angular.module('mainApp', ['timer']);
var serverAddr = '192.168.1.131:8080';
anJs = {
  routes:
   	{
  		get_controls: "http://"+ serverAddr +"/get_controls",
  		switch_state: "http://"+ serverAddr +"/switch_state",

      get_modules: "http://"+ serverAddr +"/get_modules",
      activate_module: "http://"+ serverAddr +"/activate_module",

      set_volume: "http://"+ serverAddr +"/set_volume",
  		
      get_tracks: "http://"+ serverAddr +"/get_tracks",
  		play_track: "http://"+ serverAddr +"/play_track",
      stop_track: "http://"+ serverAddr +"/stop_track",

      get_sounds: "http://"+ serverAddr +"/get_sounds",
      play_sound: "http://"+ serverAddr +"/play_sound",
      

  		current_track: "http://"+ serverAddr +"/current_track"
	}
}

app.controller('mainController',  ['$scope','$http', '$window', '$timeout', '$compile', '$interval', '$q',
  function($scope, $http, $window,  $timeout, $compile, $interval, $q) {

    // timer
    $scope.timerRunning = false;
    var timeStarted = false;
    $scope.tracksVolume = 0.5;
    $scope.countdownVal = 60 * 60; // 60 min

    $scope.startClock = function() {
      if (!timeStarted) {
          $scope.$broadcast('timer-start');
          $scope.timerRunning = true;
          timeStarted = true
      } 
      else if ((timeStarted) && (!$scope.timerRunning)) {
           $scope.$broadcast('timer-resume');
           $scope.timerRunning = true;
      }

    };

    $scope.stopClock = function() {
            if ((timeStarted) && ($scope.timerRunning)) {
                $scope.$broadcast('timer-stop');
                $scope.timerRunning = false;
            }

    };

    $scope.resetClock = function() {
            if ((!$scope.timerRunning))
                $scope.$broadcast('timer-reset');
    }

    $scope.$on('timer-stopped', function(event, data) {
            timeStarted = true;
    });

    // states
    $scope.switchState = function(control){
    	control.state = !control.state;
    	var params = {id: control.id, state: control.state ? 1 : 0}
    	$http({
        	method: 'GET',
        	url: anJs.routes.switch_state,
        	params : params
      	}).
      	success( function( data, status, headers, config ) {
        	//$scope.controls = data.controls;  
      	}).
      	error(function(data, status, headers, config) {});
    }

    $scope.activateModule = function(module){
      module.activate = !module.activate;
      var params = {id: module.id, state: module.activate ? 1 : 0}
      $http({
          method: 'GET',
          url: anJs.routes.activate_module,
          params : params
        }).
        success( function( data, status, headers, config ) {
          //$scope.controls = data.controls;  
        }).
        error(function(data, status, headers, config) {});
    }
    
    /*
    for(var i in states){
    	var state = states[i];
    	var newElement = angular.element(document.getElementById('controls-area')).
    	append($compile("<div><label>"+ state.name +"</label><button class='btn btn-default'></button></div>")($scope));
    	newElement.bind("click", function(){
    	  
	    });
	} */
	 $scope.refreshControls = function(page, preload){
      
      
      var params = {};
      

      $http({
        method: 'GET',
        url: anJs.routes.get_controls,
        params : params
      }).
      success( function( data, status, headers, config ) {
        $scope.controls = data.controls;  
      }).
      error(function(data, status, headers, config) {});
    }    

    $scope.refreshControls();
    // autorefresh
    //$interval($scope.refreshControls, 5000);

    $scope.refreshModules = function(page, preload){
      
      
      var params = {};
      

      $http({
        method: 'GET',
        url: anJs.routes.get_modules,
        params : params
      }).
      success( function( data, status, headers, config ) {
        $scope.modules = data.modules;  
      }).
      error(function(data, status, headers, config) {});
    }    

    $scope.refreshModules();

    
    $scope.refreshTracks = function(page, preload){
    	var params = {};
      
    	$http({
        	method: 'GET',
        	url: anJs.routes.get_tracks,
        	params : params
    	}).
    	success( function( data, status, headers, config ) {
        	$scope.tracks = data.tracks;  
        	//$scope.tracks['stop'] = "";

      	}).
      	error(function(data, status, headers, config) {});
    }    

    $scope.refreshTracks();

    $scope.refreshCurrentTrack = function(){
    	var params = {};
      
    	$http({
        	method: 'GET',
        	url: anJs.routes.current_track,
        	params : params
    	}).
    	success( function( data, status, headers, config ) {
        	$scope.current_track = data;  
        	//$scope.tracks['stop'] = "";

      	}).
      	error(function(data, status, headers, config) {});
    } 

    $scope.refreshCurrentTrack();
    // autorefresh
    $interval($scope.refreshCurrentTrack, 20 * 1000); // once per 20 sec

    $scope.playTrack = function(trackId){
    	var params = {trackId: trackId}
    	$http({
        	method: 'GET',
        	url: anJs.routes.play_track,
        	params : params
      	}).
      	success( function( data, status, headers, config ) {
        	
      	}).
      	error(function(data, status, headers, config) {});
    }

    $scope.stopTracks = function(trackId){
      $http({
          method: 'GET',
          url: anJs.routes.stop_track
        }).
        success( function( data, status, headers, config ) {
          
        }).
        error(function(data, status, headers, config) {});
    }


    // SOUNDS
     $scope.refreshSounds = function(page, preload){
      var params = {};
      
      $http({
          method: 'GET',
          url: anJs.routes.get_sounds,
          params : params
      }).
      success( function( data, status, headers, config ) {
          $scope.sounds = data.sounds;  

        }).
        error(function(data, status, headers, config) {});
    }    

    $scope.refreshSounds();

    $scope.playSound = function(trackId){
      var params = {trackId: trackId}
      $http({
          method: 'GET',
          url: anJs.routes.play_sound,
          params : params
        }).
        success( function( data, status, headers, config ) {
          
        }).
        error(function(data, status, headers, config) {});
    }

    //var canceler = $q.defer();
    var volumeTimer;
    $scope.volumeChange = function(){
       //canceler.resolve("cancelled"); // Resolve the previous canceler
       //canceler = $q.defer();  
      if(volumeTimer){
         $timeout.cancel( volumeTimer );
      }
      volumeTimer = $timeout(function(){
        var params = {volume: $scope.tracksVolume}
          $http({
            method: 'GET',
            url: anJs.routes.set_volume,
            params : params,
          //timeout: canceler.promise
          }).
          success( function( data, status, headers, config ) {
          
          }).
          error(function(data, status, headers, config) {});
      }, 100);    
    }

}]);


angular.module('mainApp').directive('clickPrevent', function() {
  return function(scope, element, attrs) {
    return element.on('click', function(e) {
      return e.preventDefault();
    });
  };
});