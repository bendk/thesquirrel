$(document).ready(function() {
    $("#squirrel-menu").click(function() {
        $(this).toggleClass('active');
        $(this).children('i').toggleClass('fa-caret-down fa-caret-up');
    });
    $("#expand-menu button").click(function() {
        $('nav#main > ul').toggleClass('active');
        $(this).toggleClass('active');
        return false;
    });
});

