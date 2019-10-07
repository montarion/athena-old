$(document).ready(function(){
  // sending a connect request to the server.
  var firstupdate = false;
  var socket;
  var input = document.querySelectorAll('input');
  for(i=0; i<input.length; i++){
    input[i].setAttribute('size',input[i].getAttribute('placeholder').length);
  };
  console.log("started settings script");
  if (firstupdate == false){
    socket = io.connect();
    firstupdate = true;
    socket.emit("update", "['settings']");
  };
  socket.on("settings", function(msg) {
    console.log("GETTING SETTINGS");
    console.log(msg);
    var msg = msg.values;
    var x;
    for (x in msg){
      var name = x;
      var data = msg[name];

      $('input[name=' + name + ']').val(data);
    };
  });

  $('.submitbutton').click(function logincheck (event){

    var data = {};
    var text = "";
    //$("form").serializeArray().map(function(x){data[x.name] = x.value;});
    $("legend").each( // for each legend
        function(i,e){
            var that = $(e),
                parent = that.closest("fieldset"),
                fieldname = that.text(); // get the fieldname
                var tmpdict = {}
                tmpdict[fieldname] = {}; // make a dict for that fieldname in the main dict
                console.log("looking for input fields in: " + fieldname);
                var selecfield = document.getElementById(fieldname);
                var elements = selecfield.querySelectorAll('input'); // grab all input fields
                $(elements).each(
                    function(i, e){
                        var name = e.name;
                        var val = e.value;
                        console.log("updated: " + name);
                        tmpdict[fieldname][name] = val; // and save the keypairs
                    }
                );
                data = Object.assign(data, tmpdict); //update data
            }
        );
    console.log(data);
    socket.emit("settingupdate", data);
  });
});

