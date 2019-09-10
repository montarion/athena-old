function eventupdate(text, category = "normal") {
  document.getElementById("notificationbutton").classList.remove("hidden");
  if (category == "normal") {
    var category = "anime";
  } else {
    var category = category;
  }
  var prehtml = '<div class="column"> \
                <div class="card"> \
                  <div class="cardcontent"' + category + ">"

  var posthtml = '</div><div class="time">' + gettime() + '</div></div></div>'
  var html = prehtml + text + posthtml;
  var div = document.createElement('div');
  div.innerHTML = html;
  $(div).hide().prependTo($("#sidebar")).fadeIn();
  document.getElementById("notificationbutton").classList.remove("hidden");
  if (category == "alert"){
    openMenuRight();
  };
}

function gettime(){
  var today = new Date();
  var now = today.getHours() + ":" + today.getMinutes();
  return now
};

