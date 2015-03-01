$(document).ready(function() {
    var body = $('body');

    $('fieldset.editor').each(function() {
        var fieldset = $(this);
        var textarea = $('textarea', this);
        var addMedia = $('.add-media', this);
        var addMediaProgress = $('.add-media-progress', this);
        var addMediaProgressBar = $('.bar', addMediaProgress);
        var addImage = $('button.add-image', this);
        var preview = $('button.preview', this);
        var uploadFile = $('<input type="file" name="file">');
        var uploadFileForm = $('<form>').append(uploadFile);
        body.append(uploadFileForm);

        preview.click(function() {
            var overlay = $('<div id="overlay">');
            $('body').append(overlay);
            var modal = $('#editor-preview-modal');
            modal.show();
            $('button.close', modal).click(function() {
                modal.hide();
                overlay.remove();
            });
            $.ajax({
                url: '/editor/preview/',
                type: 'GET',
                data: {
                    'body': textarea.val(),
                },
                headers: {
                    'X-CSRFToken': $.cookie('csrftoken'),
                },
                success: function(responseData) {
                    $('i.fa-spinner', modal).hide();
                    $('div.body', modal).html(responseData['body']);
                }
            });
            return false;
        });

        addImage.click(function() {
            uploadFile.click();
            return false;
        });
        uploadFile.change(function() {
            if(uploadFile.val()) {
                addMedia.hide();
                textarea.prop('disabled', true);
                addMediaProgress.show();
                uploadFileForm.ajaxSubmit({
                    url: '/editor/upload-image/',
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': $.cookie('csrftoken'),
                    },
                    uploadProgress: function(evt, pos, total, percent) {
                        addMediaProgressBar.css('width', percent + '%');
                    },
                    success: function(responseData) {
                        addMedia.show();
                        addMediaProgress.hide();
                        textarea.prop('disabled', false);
                        insertAtCaret(textarea, '#image-' + 
                            responseData['imageId'] + '-full\n\n');
                    }
                });
            }
        });
    });

    function insertAtCaret(textarea, insertText) {
        textarea = textarea[0];
        if (document.selection) {
            textarea.focus();
            sel = document.selection.createRange();
            sel.text = insertText;
            textarea.focus();
        } else if (textarea.selectionStart || textarea.selectionStart == '0') {
            var startPos = textarea.selectionStart;
            var endPos = textarea.selectionEnd;
            var scrollTop = textarea.scrollTop;
            textarea.value = (textarea.value.substring(0, startPos) +
                    insertText +
                    textarea.value.substring(endPos,textarea.value.length));
            textarea.focus();
            textarea.selectionStart = startPos + insertText.length;
            textarea.selectionEnd = startPos + insertText.length;
            textarea.scrollTop = scrollTop;
        } else {
            textarea.value += insertText;
            textarea.focus();
        }
    }
});
