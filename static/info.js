// Snackasaurus Info Page

$( document ).ready(function() {
	fetchData();

	//setTimeout(fetchData, 3000);
});

function fetchData() {
	setTimeout(fetchData, 8000);

	$('.list-group').empty();

	var xhttp = new XMLHttpRequest();
	xhttp.open("GET", "http://unimate.cs.washington.edu:59595/display", true);
	xhttp.setRequestHeader("Access-Control-Allow-Origin", "unimate.cs.washington.edu");
	xhttp.send();
	xhttp.onload = function(event)
	{
		var data = JSON.parse(xhttp.responseText);
		var i = 0;
		for (var key in data) {
			if (data.hasOwnProperty(key)) {
				//alert(key + " -> " + data[key]);
				var jobData = data[key];
				var name = jobData[0];
				var location = jobData[1];
				if (i == 0) {
					$('.list-group').append('<a class="list-group-item active">' +
					'<h4 class="list-group-item-heading">Now delivering to: '+ name +'</h4>' +
					'<p class="list-group-item-text">Location: '+location+'</p>');
					$('.list-group').append('</a>');
				} else {
					$('.list-group').append('<a class="list-group-item">' +
					'<h4 class="list-group-item-heading">' + name +'</h4>' +
					'<p class="list-group-item-text">Location: '+location+'</p>');
					$('.list-group').append('</a>');
				}
				i++;
			}
		}
	}
}

