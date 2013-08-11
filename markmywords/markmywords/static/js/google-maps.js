var infowindow;
	var map;
	var geocoder;

	function load() {
		navigator.geolocation.getCurrentPosition(userLocation, error);
	}

	var userLocation = function(pos) {
		var lat = pos.coords.latitude;
		var lng = pos.coords.longitude;
		initialize(lat, lng);
	}

	var error = function(error) {
		if (error.code === 1) {
			alert('Unable to get location');
		}
	}

	function initialize(lat, lng) {

		var mapOptions = {
			zoom: 18,
			mapTypeControl: false,
			center: new google.maps.LatLng(lat, lng),
			mapTypeId: google.maps.MapTypeId.ROADMAP
		};

		geocoder = new google.maps.Geocoder();
		map = new google.maps.Map(document.getElementById('map-canvas'),
		mapOptions);

		// var marker = new google.maps.Marker({
		// 	map: map,
		// 	position: new google.maps.LatLng(lat, lng),
		// 	zIndex: 1
		// });

		// google.maps.event.addListener(marker, 'click', function() {
		// 	if (infowindow) infowindow.close();
		// 	infowindow = new google.maps.InfoWindow({
		// 		content: generateInfo(),
		// 		maxWidth: 310
		// 	});
		// 	infowindow.open(map, marker);
		// });

		addPaths();

		function addPaths(){
			//iterate through all paths
			for(var i = 0; i < path_list.length; i++){
					// console.log("Path: " + i)
					// console.log(path_list[i])
				//iterate through all points on a path
					for(var j = 0; j < path_list[i].length; j++){	
						var coord = path_list[i][j]
						var lat = path_list[i][j][1];
						var lng = path_list[i][j][0];
						flightPlanCoordinates.push(new google.maps.LatLng(lat, lng));
					}
				// flightPlanCoordinates.push(new google.maps.LatLng(path_list[0], path_list[1]));
			}

			console.log("Flight Plan: ")
			console.log(flightPlanCoordinates)

		  var flightPath = new google.maps.Polyline({
		    path: flightPlanCoordinates,
		    strokeColor: '#FF0000',
		    strokeOpacity: 1.0,
		    strokeWeight: 2
		  });

		  	map.setCenter(new google.maps.LatLng(path_list[0][0][1], path_list[0][0][0]))
  			flightPath.setMap(map);

  			var marker = new google.maps.Marker({
			map: map,
			position: new google.maps.LatLng(path_list[0][0][1], path_list[0][0][0]),
			zIndex: 1
		});
		}

	}

	function codeAddress(place) {

		var address = place;

		geocoder.geocode({
			'address': address
		}, function(results, status) {
			if (status == google.maps.GeocoderStatus.OK) {
				map.setCenter(results[0].geometry.location);
				var marker = new google.maps.Marker({
					map: map,
					position: results[0].geometry.location
				});
			} else {
				alert("Geocode was not successful for the following reason: " + status);
			}
		});
	}

	function generateInfo() {
		text = '<div class="marker">';
		text += '<p> This is you! </p>';
		text += '</div>';
		return text;
	}

	function haversine(nlat, nlong, mlat, mlong, distance) {

		var R = 6371; // radius of earth in km
		var distances = [];
		var closest = -1;
		var dLat = rad(mlat - nlat);
		var dLong = rad(mlong - nlong);
		var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(rad(nlat)) * Math.cos(rad(nlat)) * Math.sin(dLong / 2) * Math.sin(dLong / 2);
		var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
		var d = R * c;
		if (d < distance) {
			return 1;
		} else {
			return 0;
		}
	}

	function rad(x) {
		return x * Math.PI / 180;
	}

	google.maps.event.addDomListener(window, 'load', load);