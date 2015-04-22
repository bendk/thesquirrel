(function() {
    $(document).ready(function() {
        $('input.pikaday').each(handlePikaday);
        $('form.events #id_repeat-type').each(handleRepeatSelect);
        $('form.events .exclude-list').each(handleExcludeList);
        $('table.calendar').each(handleCalendar);
    });

    function handleRepeatSelect() {
        var input = $(this);
        input.change(function() {
            if(input.val()) {
                $('form.events .details').show();
            } else {
                $('form.events .details').hide();
            }
        }).change();
    }

    function handleExcludeList() {
        var excludeList = $(this);
        var calendar = $('.calendar', excludeList);
        var closeButton = $('a.close', excludeList);
        var addButton = $('a.add', excludeList);

        var picker = new Pikaday({
            onSelect: function(date) {
                var parts = [
                    zeroPad(date.getMonth() + 1, 2),
                    zeroPad(date.getDate(), 2),
                    date.getFullYear()
                ];
                appendDate(parts.join('/'));
                calendar.hide();
            },
        });
        calendar.prepend(picker.el);

        addButton.click(function(evt) {
            calendar.show();
        });
        closeButton.click(function(evt) {
            calendar.hide();
        });

        function onRemoveClicked(evt) {
            $(this).closest('div').remove();
        };
        $('.date a', excludeList).click(onRemoveClicked);

        function appendDate(dateStr) {
            var dateElt = $('<div class="date">' + dateStr + ' </div>');
            var input = $('<input type="hidden" name="repeat-exclude">')
                .val(dateStr);
            var removeButton = $('<a class="button">').click(onRemoveClicked)
                .append($('<span class="fa fa-close">'));
            dateElt.append(input, removeButton);
            addButton.before(dateElt);
        }
    }


    function zeroPad(number, digits) {
        var str = number.toString();
        while(str.length < digits) {
            str = '0' + str;
        }
        return str;
    }

    function handlePikaday() {
        var input = $(this);
        // set readonly to disable mobile virtual keyboards
        input.prop('readonly', true);
        var picker = new Pikaday({
            trigger: input[0],
            onSelect: function(date) {
                var parts = [
            zeroPad(date.getMonth() + 1, 2),
            zeroPad(date.getDate(), 2),
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
    }

    function handleCalendar() {
        var calander = $(this);
        var dateDetails = calander.next('div.date-details');

        $('td', calander).click(function () {
            // Only handle the click on small screens;
            if($(window).width() >= 768) {
                return;
            }
            var eventList = $('ul', this);
            if(eventList.length > 0) {
                replaceDateDetails($(this).data('date-title'), eventList);
            }
        });

        function replaceDateDetails(dateTitle, eventList) {
            if(dateDetails) {
                dateDetails.remove();
            }
            var heading = $('<h3>').text(dateTitle);
            dateDetails = $('<div class="date-details">')
                .append(heading)
                .append(eventList.clone());
            calander.after(dateDetails);
        }
    }

}());
