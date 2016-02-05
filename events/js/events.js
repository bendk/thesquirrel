(function() {
    $(document).ready(function() {
        $('input.pikaday').each(handlePikaday);
        $('form.events').each(handleEventForm);
        $('table.calendar').each(handleCalendar);
    });

    function handleEventForm(form) {
        var repeatSelects = $('.repeat-form .type select', form);
        var excludeSection = $('.exclude-form', form);
        var excludeList = $('.exclude-list', form);

        mirrorEventField('start_time');
        mirrorEventField('end_time');
        mirrorEventField('date', 'start_date');
        repeatSelects.change(onRepeatTypeChange).change();
        hideExtraNewRepeatForms();
        handleExcludeList(excludeList);

        function anyRepeatEnabled() {
            return repeatSelects.is(function() {
                return $(this).val();
            });
        }

        function hideExtraNewRepeatForms() {
            $('.new-repeat-forms fieldset:gt(0)', form).hide();
            $('.new-repeat-forms :input').change(function() {
                var fieldset = $(this).closest('fieldset');
                if(repeatFormFilledIn(fieldset)) {
                    var next = fieldset.next();
                    if(next) {
                        next.show();
                    }
                }
            });
        }

        function repeatFormFilledIn(fieldset) {
            return weekdaySelected(fieldset) && datesSelected(fieldset);
        }

        function weekdaySelected(fieldset) {
            return $('.weekdays input').is(function(i, elt) {
                return $(elt).prop('checked');
            });
        }

        function datesSelected(fieldset) {
            var dateInputs = $('input.pikaday', fieldset);
            var filledInDateInputs = dateInputs.filter(function(i, elt) {
                return $(elt).val();
            });
            return filledInDateInputs.length == dateInputs.length;
        }

        function onRepeatTypeChange() {
            var selected = $(this).val();
            var repeatForm = $(this).closest('.repeat-form');;
            var detailsSection = $('.details', repeatForm);

            if(selected) {
                detailsSection.show();
                excludeSection.show();
            } else {
                detailsSection.hide();
                if(!anyRepeatEnabled()) {
                    excludeSection.hide();
                }
            }
        }

        function mirrorEventField(eventFieldName, repeatFieldName) {
            if(repeatFieldName === undefined) {
                repeatFieldName = eventFieldName;
            }

            var eventField = $('#id_event-' + eventFieldName);
            var repeatField = $('#id_repeat-create-' + repeatFieldName);
            var repeatFieldChanged = false;

            eventField.change(function() {
                if(!repeatFieldChanged) {
                    repeatField.val(eventField.val());
                }
            }).change();

            repeatField.change(function() {
                repeatFieldChanged = true;
            });
        }
    }


    function handleExcludeList(excludeList) {
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
            var input = $('<input type="hidden" name="exclude-dates">')
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
                // ensure change handlers get called
                input.change();
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
