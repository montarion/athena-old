$(document).ready(function() {
    var viewportwidth = $(window).width();
    var viewportheight = $(window).height();
    var count = $('.headbar .column').length;
    console.log(count);
    $(".headbar .column").css("width", 100 / count + "%");
    

    // sending a connect request to the server.
  var firstupdate = false;
  var socket;
  console.log("started main script");

  //restore values:
  if (localStorage){
    var ls = localStorage;
    if ("anime" in ls){
        var dict = {"type":"anime", "anime":ls.anime};
        update(dict);
        };
    if ("song" in ls){
        var dict = {"type":"song", "song":ls.song};
        console.log(ls.getItem("song"));
        update(dict);

       };
    if ("image" in ls){
        var dict = {"type":"image", "image":ls.image};
        update(dict);
        };
    if ("news" in ls){
        var dict = {"type":"news", "news":ls.news};
        update(dict);
        };
  };

  if (firstupdate == false){
    socket = io.connect();
    firstupdate = true;
    socket.emit("update", "['motd', 'anime']");
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
    var dict = {"type":"anime", "anime":msg};
    update(dict);
    localStorage.setItem("anime", msg)
  });
  socket.on("song", function(msg){
    console.log("song updated!");
    console.log(msg);
    var dict = {"type":"song", "song":msg};
    update(dict);
    console.log("updated song");
    console.log(msg);
    localStorage.setItem("song", msg);
  });
  socket.on("image", function(msg){
    console.log("image updated!");
    console.log("msg: " + msg);
    var dict = {"type":"image", "image":msg};
    update(dict);
    localStorage.setItem("image", msg);
  });
  socket.on("weather", function(msg){
    console.log("weather updated!");
    console.log("msg: " + msg);
    $(".motd-weather").text(msg);
  });
  socket.on("news", function(msg){
    console.log("news updated!");
    var dict = {"type":"news", "news":msg};
    update(dict);
    console.log(dict);
    localStorage.setItem("news", msg);
  });
  socket.on("event", function(msg){
    console.log("GOT EVENT");
    category = msg.category;
    msg = msg.msg;
    eventupdate(msg, category); //eventupdate is a function from menu2.js
  });


    //image stuff
    
    var maxheight = ((window.innerHeight * 35) / 100);
    var maxwidth = $(".main").width();
    console.log("maxheight=" + maxheight);
    console.log("maxwidth=" + maxwidth);
    
    

    var img = document.querySelector("#motd-image");
    img.onload = function() {
        var viewportheight = $(window).height();
        console.log("loaded");
        var divheight = parseInt($(".card.image").css("height"));
        var divwidth = parseInt($(".card.image").css("width"));
        var imgwidth = this.naturalWidth;
        var imgheight = this.naturalHeight
        console.log("width: " + imgwidth);
        console.log("height: " + imgheight);
        console.log("divwidth: " + divwidth);
        var aspratio = imgwidth / imgheight;
        var invaspratio = imgheight / imgwidth;
        console.log("asp " + aspratio);
        console.log("inv " + invaspratio);
        console.log(imgwidth > maxwidth);
        if (imgwidth > maxwidth || imgheight > maxheight){
            if (imgwidth > imgheight){
                //width is too big, make larger
                var newwidth = (maxheight * aspratio);
                var newheight = (newwidth * invaspratio) -20;
                console.log("newwidth1: " + newwidth);
                console.log("newheight1: " + newheight);
                
                
                newwidth = newwidth + "px";
                console.log("newwidth1: " + newwidth);
                console.log("newheight1: " + newheight);
                $(".card .image").css({"width": newwidth});
                $(".card .image").css({"height": newheight});
                $(".card.image").css({"width": newwidth});
                $(".card.image").css({"height": newheight});
            } else {
                // height is too big, make it smaller
                var newheight = (maxheight * invaspratio) - 5;
                var newwidth = (newheight * aspratio) + "px";
                newheight = newheight + "px";
                
                console.log("newwidth2: " + newwidth);
                console.log("newheight2: " + newheight);
                $(".card.image").css({"width": newwidth});
                $(".card.image").css({"height": newheight});
                $(".card .image").css({"width": newwidth});
                $(".card .image").css({"height": newheight});
            };
            //remove rest of card
            $(".card.image").css({"background-color": "#383c4a"});
            $(".card.image").css({"box-shadow": "none"});

        };
            
        
        
        
        var imgwidth = this.naturalWidth;
        var imgheight = this.naturalHeight;
        console.log(imgwidth);
        console.log(imgheight);
    };
});

function update(data){
  if (data.type == "song"){
    console.log("in song");
    data = data.song;
    source = data.link;
    $('#motd-song-text').text('');
    $('#motd-song-video').attr("src", source);
    $('#motd-song').load(document.URL +  ' #motd-song');
    };
  if (data.type == "anime"){
    $(".anime").text(data.anime);
    var msg = data.anime + " aired!";
    var category = "anime";
    eventupdate(msg, category); 
    };
  if (data.type == "image"){
    $('#motd-image-text').text('');
    $('#motd-image').attr("src", data.image);
    $('#motd-image-link').attr("href", data.image);
    $('#motd-image-link').attr("target", "_blank"); // to open in new tab
    $('#motd-image').load(document.URL +  ' #motd-image');
    var img = document.querySelector("#motd-image");
    img.onload = function(){
      var imgwidth = this.naturalWidth;
      var imgheight = this.naturalHeight;
      if (imgheight < imgwidth){ //image is in landscape
        $('#motd-image').css("height", "auto");
      } else { //image is in portrait
        $('#motd-image').css("width", "auto");
        };
      };
    };
  if (data.type == "news"){
    data = data.news;
    $(".motd-news").text(data.headline);
    var redirect = "window.open('" + "https://reddit.com" + data.newslink + "'" + ")";
    $(".motd-news").attr("onclick", redirect);
    var msg = data.headline;
    var category = "news";
    eventupdate(msg, category);

    };
};

