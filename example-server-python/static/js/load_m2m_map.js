//The tutorial used as a guide to develop this script was taken from the Google API library examples
//Listed here in this link https://developers.google.com/maps/tutorials/customizing/adding-a-legend

var teamArray= [];
var markersArray = [];
var markerCluster= null;
var count = 0;
var map; 


var red_url = 'http://maps.google.com/mapfiles/markerA.png';
var yellow_url = 'http://maps.google.com/mapfiles/marker_yellowB.png';
var green_url = 'http://maps.google.com/mapfiles/marker_greenC.png';
var purple_url = 'http://maps.google.com/mapfiles/marker_purpleD.png';
var orange_url = 'http://maps.google.com/mapfiles/marker_orangeE.png';
var white_url = 'http://maps.google.com/mapfiles/marker_whiteF.png';
var black_url = 'http://maps.google.com/mapfiles/marker_blackG.png';
var gray_url = 'http://maps.google.com/mapfiles/marker_greyH.png';
var brown_url = 'http://maps.google.com/mapfiles/marker_brownI.png';
var red2_url = 'http://maps.google.com/mapfiles/markerJ.png';

var customIconUrl = [red_url,yellow_url,green_url,purple_url,orange_url,white_url,black_url,gray_url,brown_url,red2_url]
    
function initialize() {
	var Australia = new google.maps.LatLng(-28,135); //Centre of Australia
	var mapOptions = {
		zoom: 4,
		center: Australia,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	map = new google.maps.Map(document.getElementById('map'), mapOptions);
	startTimer();
}

function startTimer(){
	setInterval(function() {
		deleteOverlays();//should delete any existing point and clear the cluster
		addMarker();
		if (count == 0) {addLegend(map);}
	},6000); // 5 second refresh
}

function addMarker() {
	$.ajax({
		type: "GET",
		url: "http://58.162.145.208:8080/api/position",
		//url: "./assets/teams.json",
		async: false,
		dataType: "json",
		success: function(data){
				teamArray = data;
			}
	});							 
		var teamIndex = 0;                       
		teamArray.forEach( function (teamObject) {
								var teamInfo = new google.maps.InfoWindow({content: '<h1>'+ teamObject.displayString + '</h1>' + 
																					'<br><p> Latitude:' + teamObject.latitude + ' , ' + 
																					'Longitude:' + teamObject.longitude + '</p>' + 
																					'<br><p> data: ' +  teamObject.arbitraryText +'</p>' //+
																					//'<br><p> IMEI:' + teamObject.imei + '</p>' + 
																					//'<br><p> IMSI:' + teamObject.imsi + '</p>' + 
																					//'<br><p> Raspberry Pi Identifier:' + teamObject.cpuID + '</p>' 
																					}  
																					);
								var teamMarker = new google.maps.Marker( {
										  position: new google.maps.LatLng(teamObject.latitude, teamObject.longitude),    
										  map: map,
										  title: 'Team ' + teamIndex,
										  icon: new google.maps.MarkerImage(customIconUrl[teamIndex])
										  });
								markersArray.push(teamMarker);                               
								google.maps.event.addListener(teamMarker, 'click', function() {
										  teamInfo.open(map,teamMarker);
										  });
								teamIndex++; 
							}) 
		
		markerCluster = new MarkerClusterer(map, markersArray);			
}

// Deletes all markers in the array by removing references to them
function deleteOverlays() {
  if (markersArray.length > 0) {
	for (i in markersArray) {
	  markersArray[i].setMap(null);
	}
	markersArray.length = 0;
  }
  
	if(markerCluster!= null) {
		markerCluster.clearMarkers();
	}
}
// Shows any overlays currently in the array 
function showOverlays() { 
	  if (markersArray) { 
		for (i in markersArray) {
			markersArray[i].setMap(map);		
			} 
		} 
}
  // Initialize the legend 
function addLegend(map) {
	count++;  
	var legendWrapper = document.createElement('div'); 
	legendWrapper.id = 'legendWrapper'; 
	legendWrapper.index = 1; 
	map.controls[google.maps.ControlPosition.LEFT_BOTTOM].push(legendWrapper); 
	legendContent(legendWrapper, 'Legend'); 
	} 

  // Update the legend content 
  function updateLegend(column) { 
	var legendWrapper = document.getElementById('legendWrapper'); 
	var legend = document.getElementById('legend'); 
	legendWrapper.removeChild(legend); 
	legendContent(legendWrapper, column); 
  } 

  //Generate the content for the legend 
  function legendContent(legendWrapper, column) { 
	var legend = document.createElement('div'); 
	legend.id = 'legend'; 

	var title = document.createElement('p');
	title.innerHTML = 'Teams';
	legend.appendChild(title);
	
	var teamIndex = 0; 
	teamArray.forEach( function (teamObject){
	  var legendItem = document.createElement('div');
	  var name = document.createElement('span');
	  var icon = document.createElement('span'); 
	  name.innerHTML = teamObject.displayString;
	  icon.innerHTML = '<img src="' + customIconUrl[teamIndex] + '"> ';
	  legend.appendChild(icon);
	  legend.appendChild(name);
	  legend.appendChild(legendItem);
	  //As there are currently only 10 markers available, below code is to ensure
	  //when there are more then 10 teams that the markers are recycled.
	  if (teamIndex < 9) {teamIndex++;} else {teamIndex = 0;} 
	}) 
	
	legendWrapper.appendChild(legend);
   }  
