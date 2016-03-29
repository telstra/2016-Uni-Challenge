var teamArray = [];
var markersArray = [];
var markerCluster = null;
var count = 0;
var map; 

var a_url = 'http://maps.google.com/mapfiles/markerA.png';
var b_url = 'http://maps.google.com/mapfiles/marker_yellowB.png';
var c_url = 'http://maps.google.com/mapfiles/marker_greenC.png';
var d_url = 'http://maps.google.com/mapfiles/marker_purpleD.png';
var e_url = 'http://maps.google.com/mapfiles/marker_orangeE.png';
var f_url = 'http://maps.google.com/mapfiles/marker_whiteF.png';
var g_url = 'http://maps.google.com/mapfiles/marker_blackG.png';
var h_url = 'http://maps.google.com/mapfiles/marker_greyH.png';
var i_url = 'http://maps.google.com/mapfiles/marker_brownI.png';
var j_url = 'http://maps.google.com/mapfiles/markerJ.png';
var k_url = 'http://maps.google.com/mapfiles/markerK.png';
var l_url = 'http://maps.google.com/mapfiles/marker_yellowL.png';
var m_url = 'http://maps.google.com/mapfiles/marker_greenM.png';
var n_url = 'http://maps.google.com/mapfiles/marker_purpleN.png';
var o_url = 'http://maps.google.com/mapfiles/marker_orangeO.png';
var p_url = 'http://maps.google.com/mapfiles/marker_whiteP.png';
var q_url = 'http://maps.google.com/mapfiles/marker_blackQ.png';
var r_url = 'http://maps.google.com/mapfiles/marker_greyR.png';
var s_url = 'http://maps.google.com/mapfiles/marker_brownS.png';
var t_url = 'http://maps.google.com/mapfiles/markerT.png';
var u_url = 'http://maps.google.com/mapfiles/markerU.png';
var v_url = 'http://maps.google.com/mapfiles/marker_yellowV.png';
var w_url = 'http://maps.google.com/mapfiles/marker_greenW.png';
var x_url = 'http://maps.google.com/mapfiles/marker_purpleX.png';
var y_url = 'http://maps.google.com/mapfiles/marker_orangeY.png';
var z_url = 'http://maps.google.com/mapfiles/marker_whiteZ.png';

var customIconUrl = [a_url, b_url, c_url, d_url, e_url, f_url, g_url, h_url, i_url, j_url, k_url, l_url,
 m_url, n_url, o_url, p_url, q_url, r_url, s_url, t_url, u_url, v_url, w_url, x_url, y_url, z_url]


function jsonCallback(data){
					
				//console.log(typeof data)
				console.log('Callback stuff')
				teamArray= data;
				console.log(teamArray)
                		trimRecords();
				addLegend(map);             
		                addMarker(); 
			}


function initialize() {
	var Australia = new google.maps.LatLng(-28,135); //Centre of Australia
	var mapOptions = {
		zoom: 4,
		center: Australia,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	map = new google.maps.Map(document.getElementById('map'), mapOptions);
	$.ajax({
		type: "GET",
		// url: "http://example.innovation.telstra.com/api/position",
		url: "http://tuc.innovation.telstra.com/api/position",
		async: true,
     		jsonpCallback: 'jsonCallback',
		contentType: "application/json",
		dataType: "json",
        	success: jsonCallback
	});							
}

// Trim the list of records so that there is only one record per CPU id.
// This prevents the map being flooded by many posts from the same device, resulting 
// map displays only the most recent location post by each team.
function trimRecords() {
                var trimmedArray = [];
                var replacer = null;
                
                if (trimmedArray.length < 1 ) {trimmedArray.push(teamArray[0]);} 
                
                for (var i = 0; i < teamArray.length; i++) {                         
                                
                                for (var j = 0; j < trimmedArray.length; j++) {
                                
                                            if ((teamArray[i].cpu_ID ==  trimmedArray[j].cpu_ID) ){
                                                           replacer = null;
                                                           break;
                                            }                                            
                                            else {                                                     
                                                            replacer = teamArray[i];                                                            
                                            }
                                }
                     if (replacer != null ) {trimmedArray.push(replacer);} 
                }
				// reversed array so that teams will keep the same makers as more teams post to the map
                teamArray = trimmedArray.reverse();
}


function addMarker() { 
		var teamIndex = 0;                       
		teamArray.forEach( function (teamObject) {
							// Create marker onClick() info 
								var teamInfo = new google.maps.InfoWindow({content: '<h3>'+ teamObject.display_string + '</h3>' + 
																					'<br><p> Latitude:' + teamObject.lat + ' , ' + 
																					'Longitude:' + teamObject.lon + '</p>' + 
																					'<br>' //+
																					//'<br><p> IMEI:' + teamObject.imei + '</p>' + 
																					//'<br><p> IMSI:' + teamObject.imsi + '</p>' + 
																					//'<br><p> Raspberry Pi Identifier:' + teamObject.cpuID + '</p>' 
																					}  
																					);
//console.log(teamObject)

								var teamMarker = new google.maps.Marker( {
										  position: new google.maps.LatLng(teamObject.lat, teamObject.lon),    
										  map: map,
										  title: 'Team ' + teamIndex,
										  icon: new google.maps.MarkerImage(customIconUrl[teamIndex])
										  });
                                          teamMarker.setAnimation(google.maps.Animation.DROP);
								markersArray.push(teamMarker);                               
								google.maps.event.addListener(teamMarker, 'click', function() {
										  teamInfo.open(map,teamMarker);
										  });
								teamIndex++; 
							}) 
		
		markerCluster = new MarkerClusterer(map, markersArray, {maxZoom: 13});			
}

  // Initialize the legend 
function addLegend(map) {
	count++;  
	var legendWrapper = document.createElement('div'); 
	legendWrapper.id = 'legendWrapper'; 
	legendWrapper.index = 1; 
	map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(legendWrapper); 
	legendContent(legendWrapper, 'Legend'); 
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
      legendItem.id = 'legendItem'; 
	  var name = document.createElement('span');
	  var icon = document.createElement('span'); 
      icon.id = 'legendIcon'; 
	  name.innerHTML = teamObject.display_string.substring(0,31);
	  icon.innerHTML = '<img src="' + customIconUrl[teamIndex] + '"  > ';
	  legend.appendChild(icon);
	  legend.appendChild(name);
	  legend.appendChild(legendItem);
	  //As there are currently only x markers available, below code is to ensure
	  //when there are more then x teams that the markers are recycled.
          if (teamIndex < customIconUrl.length-1 ) {teamIndex++;} else {teamIndex = 0;} 
	}) 
	
	legendWrapper.appendChild(legend);
}  
