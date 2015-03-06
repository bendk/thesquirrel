(function() {

$(document).ready(function() {
    var page = calcPage();
    $('a.show-more, button.show-more').click(function() {
        var button = $(this);
        button.css('min-width', button.css('width'));
        var contents = button.contents().remove();
        button.append('&nbsp;<i class="fa fa-spin fa-spinner"></i>&nbsp;');
        $.ajax({
            data: {
                page: ++page,
            },
            success: function(data) {
                button.before(data['page']);
                if(data['has_next']) {
                    button.contents().remove();
                    button.css('min-width', null);
                    button.append(contents);
                } else {
                    button.remove();
                }
            }
        });
    });
});

function calcPage() {
    var match = /[?&]page=(\d+)/.exec(window.location.href);
    if(match) {
        return match[1];
    } else {
        return 1;
    }
}

}());
