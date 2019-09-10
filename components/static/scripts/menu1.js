$(document).ready(function(){
  $("#sidemenu-left").mouseover(function(){
    openMenuLeft();
    });
  $("#sidemenu-left").mouseout(function(){
    closeMenuLeft();
    });

});

/* Set the width of the side navigation to 250px */
function openMenuLeft() {
  document.getElementById("sidemenu-left").style.width = "250px";
  document.getElementById("sidemenu-left").style.opacity = 1;
}

/* Set the width of the side navigation to 0 */
function closeMenuLeft() {
  document.getElementById("sidemenu-left").style.width = "20px";
  document.getElementById("sidemenu-left").style.opacity = 0.2;
}

