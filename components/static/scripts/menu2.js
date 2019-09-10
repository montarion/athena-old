$(document).ready(function(){
  $("#sidemenu-right").mouseover(function(){
    openMenuRight();
    });
  $("#sidemenu-right").mouseout(function(){
    closeMenuRight();
    });

});

/* Set the width of the side navigation to 250px */
function openMenuRight() {
  document.getElementById("notificationbutton").classList.add("hidden");
  document.getElementById("sidebar").style.opacity = 1;
  document.getElementById("sidemenu-right").style.width = "20vw";
  document.getElementById("sidemenu-right").style.opacity = 1;
}

/* Set the width of the side navigation to 0 */
function closeMenuRight() {
  document.getElementById("sidebar").style.opacity = 0;
  document.getElementById("sidemenu-right").style.width = "20px";
  document.getElementById("sidemenu-right").style.opacity = 0.2;
}
/*
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
*/
