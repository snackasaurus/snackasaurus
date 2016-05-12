// Snackasaurus UI
$( document ).ready(function() {
    $( '#submit' ).click(function() {
      var name = $( '#name' ).val();
      var loct = $( '#location option:selected' ).text();
      var snacks = {snack1 : 0, snack2 : 0,
                    snack3 : 0, snack4 : 0,
                    snack5 : 0, snack6 : 0};
      var snacks_str = ''
      jQuery.each(obj, function(i, val) {
        snacks_str += i + '-' + val + ',';
      });
      if (snacks_str[snacks_str.length - 1] == ',') {
        snacks_str = snacks_str.substring(0, snacks_str.length - 1);
      }
      console.log(name);
      console.log(loct);
      console.log(snacks_str);
      $.get( 'attu.cs.washington.edu:50000', { name: name, location : loct,
                                               sncaks: snacks_str
      }, function(data) {
        var code = data.code;
        // do something to display the code
      });
    });
});
