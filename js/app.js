var app = angular.module('mainApp', []);

anJs = {
  routes:
   	{
  		get_controls: "http://192.168.1.239:8080/get_controls",
  		switch_state: "http://192.168.1.239:8080/switch_state",
  		get_tracks: "http://192.168.1.239:8080/get_tracks",
  		play_track: "http://192.168.1.239:8080/play_track",
  		current_track: "http://192.168.1.239:8080/current_track"
	}
}

app.controller('mainController',  ['$scope','$http', '$window', '$timeout', '$compile', '$interval',
  function($scope, $http, $window,  $timeout, $compile, $interval) {
    
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

    
    $scope.refreshTracks = function(page, preload){
    	var params = {};
      
    	$http({
        	method: 'GET',
        	url: anJs.routes.get_tracks,
        	params : params
    	}).
    	success( function( data, status, headers, config ) {
        	$scope.tracks = data.tracks;  
        	$scope.tracks['stop'] = "";

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
    $interval($scope.refreshCurrentTrack, 5000);   

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

}]);


angular.module('mainApp').directive('clickPrevent', function() {
  return function(scope, element, attrs) {
    return element.on('click', function(e) {
      return e.preventDefault();
    });
  };
});