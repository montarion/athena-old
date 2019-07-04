$(document).ready(function(){
  // sending a connect request to the server.
  var firstupdate = false;
  var socket;
  console.log("started main script");
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
  socket.on("anime", function(msg){
    firstupdate = true;
    console.log("anime updated!");
    console.log("msg: " + msg);
    $(".anime").text(msg);
  });
  socket.on("song", function(msg){
    console.log("song updated!");
    console.log(msg);
    source = msg.link;
    console.log("msg: " + msg);
    $('#motd-song-text').text('');
    $('#motd-song-video').attr("src", source);
    $('#motd-song').load(document.URL +  ' #motd-song');
    // also change background
    $('body').attr("background-image", "url('" +source + "')");
    $('body').load(document.URL + 'body');
    //$(".motd-song").text(msg);
  });
  socket.on("image", function(msg){
    console.log("image updated!");
    console.log("msg: " + msg);
    $('#motd-image-text').text('');
    $('#motd-image').attr("src", msg);
    $('#motd-image-link').attr("href", msg);
    $('#motd-image').load(document.URL +  ' #motd-image');
    console.log("added");
  });
  socket.on("weather", function(msg){
    console.log("weather updated!");
    console.log("msg: " + msg);
    $(".motd-weather").text(msg);
  });
  socket.on("news", function(msg){
    console.log("news updated!");
    console.log(msg);
    console.log(msg.newslink);
    headline = msg.headline;
    link = msg.newslink;
    console.log("headline: " + headline);
    $(".motd-news").text(headline);
    //var redirect = "window.location='" + "https://reddit.com" + link + "'";
    var redirect = "window.open('" + "https://reddit.com" + link + "'" + ")";
    console.log(redirect);
    //$(".motd-news").fadeOut(function(){
      //$(".motd-news").text(headline)}).fadeIn();
    $(".motd-news").attr("onclick", redirect);
    //$('.motd-news').load(document.URL +  ' #motd-news');

  });

});

