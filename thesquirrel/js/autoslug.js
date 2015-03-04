(function() {

$(document).ready(function() {
    $('input#id_slug[data-slug-for]').each(function() {
        var slug = $(this);
        var source = $('input#id_' + slug.data('slug-for'));
        var changed = false;

        function checkChanged() {
            if(slug.val() != URLify(source.val(), 255)) {
                changed = true;
            }
        }
        checkChanged();
        slug.change(checkChanged);

        source.keyup(function() {
            if(!changed) {
                slug.val(URLify(source.val()));
            }
        });
    });
});

}());
