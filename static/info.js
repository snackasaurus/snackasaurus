// Snackasaurus UI
$( document ).ready(function() {
  setTimeout(function () {
    var json = [];
    $('.list-group').empty();
    var i = 0;
    $.getJSON("localhost:59595/info", function(data){
      $.each(data, function(obj) {
          var name = obj['name'];
          var location = obj['location'];
          if (i == 0) {
            $('.list-group').append('<a href="#" class="list-group-item active">' +
            '<h4 class="list-group-item-heading">Now delivering to: '+ name +'</h4>' +
            '<p class="list-group-item-text">Location: '+location+'</p>')
            $('.list-group').append('</a>')
          } else {
            $('.list-group').append('<a href="#" class="list-group-item">' +
            '<h4 class="list-group-item-heading">' + name +'</h4>' +
            '<p class="list-group-item-text">Location: '+location+'</p>')
            $('.list-group').append('</a>')
          }
          i++;
      });
    });
  }, 60000);
});
