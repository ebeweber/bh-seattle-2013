$(document).ready(function() {

	var distance = $("#distance");
	var pledge = $("#pledge");
	// .focus();
	distance[0].selectionStart = distance[0].selectionEnd =0;


	//event listeners
	pledge.click(function(){
		var distance = encodeURIComponent($('#distance')[0].value
			.replace(/(^[\s]+|[\s]+$)/g, ''));
		var date = encodeURIComponent($('#date')[0].value);
		var amt = $('#amt')[0].value;
		amt = encodeURIComponent(amt.substring(1, amt.length));
		
			window.location="http://localhost:8000/paypal?distance=" + distance + 
			"&date=" + date + "&amt=" + amt;
	})

	// pledge.hover(function(){
	// 	$(this).css({ "background-image": "url('../img/pledgeBgHover.jpg')" });
	// })
});