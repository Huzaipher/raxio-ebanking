// dashboard.js - linked at the bottom of base.html with {% static 'js/dashboard.js' %}
// here we make the Menu button open and close the sidebar on small screens

// this function runs when the Menu button is clicked
function toggleSidebar() {
    // classList.toggle adds the class if it is missing and removes it if it is there. dashboard.css slides the sidebar in while <body> has "sidebar-open".
    document.body.classList.toggle("sidebar-open");
}

// here we find the Menu button by its id and run toggleSidebar() each time it is clicked
var menuButton = document.querySelector("#menu-toggle");
if (menuButton) {
    menuButton.addEventListener("click", toggleSidebar);
}
