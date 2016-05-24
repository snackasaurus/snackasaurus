// Snackasaurus UI
$( document ).ready(function() {
   var ws = new WebSocket("http://localhost:48101");
   ws.onopen = function() {
      console.log("y");
   }

   ws.onmessage = function(e) {
      console.log(e);
   }
});
