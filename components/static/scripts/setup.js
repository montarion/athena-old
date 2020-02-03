$( document ).ready(function() {
    var viewportwidth = $(window).width();
    var viewportheight = $(window).height();

    // sending a connect request to the server.
    var firstupdate = false;
    var socket;
    console.log("started main script");

    
    //initialize flickity.
    $('.main-carousel').flickity({
      // options
      cellAlign: 'left',
      contain: false,
      freeScroll: true,
      pagedots: true
    });

    var carousel = $('.main-carousel').flickity();
    //switch to cell
    carousel.flickity( 'select', 0 );
    
    $( "#greeting-next1" ).click(function(event) {
        event.preventDefault();
      $("#name").hide("slow");
      $("#location").show("slow");
      var fname = $('input[name="fname"]').val();
      var lname = $('input[name="lname"]').val();
      console.log(fname);
      $("#username").text(fname.substr(0,1).toUpperCase()+fname.substr(1));
    });
    
    $( "#greeting-next2" ).click(function(event) {
        event.preventDefault();
      $("#location").hide("slow");
      $("#greeting-submit").show("slow");
    });
    
    $("#greeting-submit").click(function( event ) {
        event.preventDefault();
        msg = {"greeting":$("#greeting").serializeJSON()};
        console.log(msg);
        sendmsg(msg);
        msg = {"busstops":""}
        sendmsg(msg);
        console.log("moving on now!");
        carousel.flickity("next")
    });
    
    $( "#work-next1" ).click(function(event) {
        event.preventDefault();
      var ls = localStorage;
      var busstops = JSON.parse(ls.getItem("busstops"));
      console.log(busstops);
      for (let key in busstops){ // let here is necessary to make the click registration work
        console.log(busstops[key]);
        var name = busstops[key]["name"];
        var direction = busstops[key]["direction"];
        $("#busselector").append("<div class=\"card\" id=" + key + ">" + name + " in direction: " + direction + "</div><br>");
        $("#"+key).click(function(event){
          console.log(busstops[key]["name"] + " was clicked!");
          //confirm choice at some point
          alert("you picked:" + busstops[key]["name"]);
        });
      };
      //for {
      //$("#busselector").append("<div class=\"card\">test" + i + "</div><br>");
      //}

      $("#worklocation").hide("slow");
      $("#buslocation").show("slow");
  });

});

