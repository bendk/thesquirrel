$(document).ready(function() {
    $("#squirrel-menu").click(function() {
        $(this).toggleClass('active');
        $(this).children('i').toggleClass('fa-caret-down fa-caret-up');
    });
});

