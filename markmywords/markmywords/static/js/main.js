$(document).ready(function() {

	var distance = $("#distance");
	var pledge = $("#pledge");
	// .focus();
	distance[0].selectionStart = distance[0].selectionEnd =0;


	//event listeners
	pledge.click(function(){
		window.location="http://google.com";
	})

	// pledge.hover(function(){
	// 	$(this).css({ "background-image": "url('../img/pledgeBgHover.jpg')" });
	// })
});