function eventupdate(text, type = "normal") {
  if (type == "normal") {
    var category = "anime";
  } else {
    var category = "anime";
  }
  var html = "<div class=\"column\"> \
                <div class=\"card\"> \
                  <div class=\"cardcontent \"" + category + ">" +
                     text +
                  "</div> \
                </div> \
              </div>"


  console.log(html);
  var div = document.createElement('div');
  div.innerHTML = html;
  document.getElementById("sidebar").prepend(div);
}
