$(document).ready(function() {
	var at = $("#access_token")[0].innerHTML;
	var goal_id_val = $("#goal_id")[0].innerHTML;

	setInterval(function(){
		// Update the information using the access token
		$.get("http://127.0.0.1:8000/update/goal/" + goal_id_val + "/",
			{'access_token': at},
			 function(data) { 
				


				$("#distance")[0].innerHTML = data.current_progress
				$("#percentage")[0].innerHTML = Math.floor(data.percent_completed)
				playerOneValue = Math.floor(data.percent_completed)
				$('#progressOne').text(playerOneValue + "%");
				$("#playerOne").progressbar("value", playerOneValue)
				console.log("Successs");
			 

			 });}, 3000);
});