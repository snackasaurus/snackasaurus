// Snackasaurus UI
$( document ).ready(function() {
    $( '#place-order' ).click(function() {

      //alert("hello");
      var name = $( '#clientname' ).val();
      var loct = $( '#location option:selected' ).text();
      
      var snickers = document.getElementById('snickers').checked
      var snickersAmount = $( '#snicker_amount option:selected' ).text();
      
      var cheetos = document.getElementById('cheetos').checked
      var cheetosAmount = $( '#cheetos_amount option:selected' ).text();

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
      var xhttp = new XMLHttpRequest();
      xhttp.open("GET", "http://unimate.cs.washington.edu:59595/order?name=" + name + "&location=" + loct, true);
      xhttp.setRequestHeader("Access-Control-Allow-Origin", "http://unimate.cs.washington.edu:59595");
      xhttp.send();
      xhttp.onload = function(event)
      {
        var json = xhttp.responseText; // Response, yay!
        console.log(json)
      }
    });
});
