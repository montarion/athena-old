    $(document).ready(function() {
        var h = $(window).height();
        var w = $(window).width();
        var socket = io.connect({'multiplex': false});
        socket.on("connected", function(msg) {
            console.log("gatekeeper fired");
            console.log(msg);
            var obj = JSON.parse(JSON.stringify(msg.data)) //get acutal json that was sent(as string)
            var data = JSON.parse(obj) //parse the string you got.
            var list = Object.values(data.connected)
            
            namelist = "";
            for (var name in list) {
                var name = data;
                console.log(list)
            }

            $('.connected').html('<div>' + list + '</div>');
        });
        socket.on("anime", function(msg) {
            console.log("anime fired")
            var obj = JSON.parse(JSON.stringify(msg.data)) //get acutal json that was sent(as string)
            var data = JSON.parse(obj) //parse the string you got.
            var anilist = "";
            var number = 1;
            for (var key in data.anime) {
                var title = key;
                var link = data.anime[title][0];
                var poster = data.anime[title][1];
                console.log(poster)
                //var realposter = ("{{ url_for('static', filename='files/anime/" + poster + "')}}")

                //anilist += "<div class=\"hoverable slider closed\" id=\"slider" + number + "\"" + ">" + title + "<a href" + "=" + link +" target=\"_blank\" ><img src=" +  poster + "></a><div class=\"centertext\">" + title + "</div>hey</div>";
                anilist += "<div class=\"container" + number + "\" style=\"position: relative\" ><div class=\"hoverable slider closed tinted\"id=\"slider" + number + "\"><a href" + "=" + link +" target=\"_blank\" style=\"text-decoration: none\"><img class=\"image\" src="+ poster + "></div><div class=\"centertext\">" + title + "</div></div></div>"
                number += 1;
            }
            $('.anime').html(anilist);
            hoveranime();
        });
        socket.on("gatekeeper", function(msg) {
            console.log("gatekeeper fired")
            var obj = JSON.parse(JSON.stringify(msg.data)) //get acutal json that was sent(as string)
            var data = JSON.parse(obj) //parse the string you got.
            namelist = "";
            for (var key in data) {
                var name = key
                var status = data[name]
                console.log(status)
                namelist+= "<div class=\"fly\" id=" + name + "\"" + "><p>" + name + " : " + status + "</p></div>";
            }
            $('.gatekeeper').html(namelist);
        });
        socket.on("background", function(msg) {
            console.log("background fired")
            var obj = JSON.parse(JSON.stringify(msg.data)) //get acutal json that was sent(as string)
            var data = JSON.parse(obj) //parse the string you got.
            console.log(data)
            for (var key in data) {
                var name = key
                var link = data[name]
                img = new Image();
                img.src = link;
                img.onload = function(){
                    var canvas = document.getElementById("canvas");
                    var ctx = canvas.getContext('2d');
                    canvas.width=w
                    canvas.height=h
                    ctx.drawImage(img, 0, 0, w, h);
                    document.body.appendChild(canvas);
                    console.log("done!")
                };

                //$("body").css("background-image", "url(\"" + link + "\")");
            }
        });
    });

    function hoveranime() {
        $(".hoverable").hover(
            function () { //on hover
                document.getElementById(this.id).classList.toggle("closed");
                $(this).parent().siblings().children(".hoverable").toggleClass( "nonactive" );
                document.getElementById(this.id).classList.toggle("tinted");

            }, function() {//off hover
                document.getElementById(this.id).classList.toggle("closed");
                $(this).parent().siblings().children(".hoverable").toggleClass( "nonactive" );
                document.getElementById(this.id).classList.toggle("tinted");
        });
    }

