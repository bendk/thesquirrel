(function() {

$(document).ready(function() {
    $('form .submits-form').keypress(function(evt) {
        if(evt.which == 13 && !evt.shiftKey) {
            evt.preventDefault();
            evt.stopPropagation();
            $(this).closest('form').submit();
        }
    });
});

}());
