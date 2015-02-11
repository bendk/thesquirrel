$(document).ready(function() {
    $("#menu-toggle button").click(function() {
        $(this).toggleClass('close');
        $('nav#main').toggleClass("open");
    });
});
