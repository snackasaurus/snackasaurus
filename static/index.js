// Snackasaurus UI
$( document ).ready(function() {
    $( '#place-order' ).click(function() {

      //alert("hello");
      var name = $( '#clientname' ).val();
      var loct = $( '#location option:selected' ).text();

      var snacks_str = "";

      var snickers = document.getElementById('snickers').checked
      if (snickers) {
        snacks_str += "&snickers=" + $( '#snicker_amount option:selected' ).text();
      }

      var cheetos = document.getElementById('cheetos').checked
      if (cheetos) {
        snacks_str += "&cheetos=" + $( '#cheetos_amount option:selected' ).text();
      }

      var mandms = document.getElementById('mandms').checked
      if (mandms) {
        snacks_str += "&mandms=" + $( '#mandms_amount option:selected' ).text();
      }

      var twix = document.getElementById('twix').checked
      if (twix) {
        snacks_str += "&twix=" + $( '#twix_amount option:selected' ).text();
      }

      var doritos = document.getElementById('doritos').checked
      if (doritos) {
        snacks_str += "&doritos=" + $( '#doritos_amount option:selected' ).text();
      }

      var skittles = document.getElementById('skittles').checked
      if (skittles) {
        snacks_str += "&skittles=" + $( '#skittles_amount option:selected' ).text();
      }

      alert(snacks_str);

      //var snacks = {snack1 : 0, snack2 : 0,
       //             snack3 : 0, snack4 : 0,
       //             snack5 : 0, snack6 : 0};
      //var snacks_str = ''
      //jQuery.each(obj, function(i, val) {
      //  snacks_str += i + '-' + val + ',';
      //});
      //if (snacks_str[snacks_str.length - 1] == ',') {
      //  snacks_str = snacks_str.substring(0, snacks_str.length - 1);
      //}
      console.log(name);
      console.log(loct);
      //console.log(snacks_str);
      //$.get('localhost:59595/order', { name: name, location : loct }).done(function (data) {
      //    alert("");
      //});

      //$.get('http://unimate.cs.washington.edu:59595', function(data) {
      //    alert("");
      //});

      //$.get( 'attu4.cs.washington.edu:59595', { name: name, location : loct });
                                               //sncaks: snacks_str
      var code = Math.floor(Math.random()*9000) + 1000;

      var xhttp = new XMLHttpRequest();
      xhttp.open("GET", "http://unimate.cs.washington.edu:59595/order?name=" + name + "&location=" + loct + "&code=" + code + snacks_str, true);
      xhttp.setRequestHeader("Access-Control-Allow-Origin", "http://unimate.cs.washington.edu:59595");
      xhttp.send();
      xhttp.onload = function(event)
      {
        var json = xhttp.responseText; // Response, yay!
        console.log(json)
        document.getElementById("body").innerHTML = " " + json
        alert("Your code is " + code);
      }
    });
});



// testing things out
function handleCheckbox(cb, amount_id) {
  if (cb.checked) {
    document.getElementById(amount_id).disabled = false
  } else {
    document.getElementById(amount_id).disabled = true
    document.getElementById(amount_id).value = 0
  }
}

