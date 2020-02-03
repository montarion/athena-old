var socket;
$(document).ready(function() {
    var viewportwidth = $(window).width();
    var viewportheight = $(window).height();
    var firstupdate = false;
    console.log("started setup networking script");

if (firstupdate == false){
    socket = io.connect();
    firstupdate = true;
  };
  socket.on("message", function(msg){
    console.log(msg);
  });
  socket.on("disconnect", function(msg){
    console.log("DISCONNECTED");
    console.log("disconnected");
  });
  socket.on("bussetup", function(msg){
    console.log(msg);
    localStorage.setItem("busstops", JSON.stringify(msg))
  });
});

function sendmsg(msg){
    socket.emit("setupupdate", msg);
}

