
function setupnetwork(resolve, reject){

$(document).ready(function() {
    var viewportwidth = $(window).width();
    var viewportheight = $(window).height();
    var firstupdate = false;
    console.log("started setup networking script");

if (firstupdate == false){
    //var socket;
    socket = io.connect();
    socket.connect();
    console.log(socket.connected)
    console.log("Connected!");
    firstupdate = true;
    //mainnetworking(socket);
    resolve(socket)
};
});
}
