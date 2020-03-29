console.log("loaded.");

//get the mouseover shade effect for anime
$(document).ready(function(){
  console.log("READY");
  $(".animecard").hover(function(){
  $(this).find(".animeshade").show();
  $(this).find(".animetext").show();
    }, function(){
    $(this).find(".animeshade").hide();
    $(this).find(".animetext").hide();
  });


  //socketio connection
  console.log("Starting networking");
  console.log("promise test");
  var socket;
  const myPromise = new Promise(function(resolve, reject) {
    socket = setupnetwork(resolve, reject);
  });

  myPromise.then(
    result => mainnetworking(),
    error => console.log(error)
  );
  //var socket = setupnetwork();
  //console.log("moving to main!");
  //mainnetworking();
});
