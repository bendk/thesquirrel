(function() {
    function zeroPad(number, digits) {
        var str = number.toString();
        while(str.length < digits) {
            str = '0' + str;
        }
        return str;
    }

    $(document).ready(function() {
        $('input.pikaday').each(function() {
            var input = $(this);
            // set readonly to disable mobile virtual keyboards
            input.prop('readonly', true);
            var picker = new Pikaday({
                trigger: input[0],
                onSelect: function(date) {
                    var parts = [
                        zeroPad(date.getMonth() + 1, 2),
                        zeroPad(date.getDay() + 1, 2),
                        date.getFullYear()
                    ];
                    input.val(parts.join('/'));
                    picker.hide();
                },
            });
            input.after(picker.el);
            picker.hide()
            input.click(function() {
                if(picker.isVisible()) {
                    picker.hide();
                } else {
                    picker.show();
                    picker.adjustPosition();
                    $(picker.el).css('width', input.css('width'));
                }
            });
        });
    });


}());
