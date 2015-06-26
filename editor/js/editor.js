$(document).ready(function() {

var body = $('body');

$('fieldset.editor').each(function() {
    var fieldset = $(this);
    var textarea = $('textarea', this);

    editorUploadImage(fieldset, textarea);
    editorPreview(fieldset, textarea);
});

function editorUploadImage(fieldset, textarea) {
    var addMedia = $('.add-media', fieldset);
    var addMediaProgress = $('.add-media-progress', fieldset);
    var addMediaProgressBar = $('.bar', addMediaProgress);
    var uploadImage = $('button.upload-image', fieldset);
    var copyImage = $('button.copy-image', fieldset);
    var uploadFile = $('<input type="file" name="file">');
    var uploadFileForm = $('<form>').append(uploadFile);
    body.append(uploadFileForm.hide());

    uploadImage.click(function() {
        uploadFile.click();
        return false;
    });
    copyImage.click(function() {
        var url = window.prompt(copyImage.data('prompt'));
        if(!url) {
            return false;
        }
        textarea.prop('disabled', true);
        $.ajax({
            type: 'POST',
            url: '/editor/copy-image/',
            data: { 'url': url },
            headers: {
                'X-CSRFToken': $.cookie('csrftoken'),
            },
            success: function(responseData) {
                textarea.prop('disabled', false);
                if(responseData['imageId']) {
                    insertImageTag(responseData['imageId']);
                }
            }
        });
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
                    if(responseData['imageId']) {
                        insertImageTag(responseData['imageId']);
                    }
                }
            });
        }
    });

    function insertImageTag(imageId) {
        var toInsert = '#image-' + imageId + '-full';
        var text = textarea.val();
        if(textarea[0].selectionStart) {
            var pos = textarea[0].selectionStart;
        } else {
            var pos = 0;
        }
        function lineStartAt(pos) {
            return (pos < 1 || pos > text.length || text[pos-1] == "\n");
        }
        // Move forward until we find a newline
        while(!lineStartAt(pos)) {
            pos++;
        }
        // Check if we need to add newline before
        if(!lineStartAt(pos-1)) {
            toInsert = '\n' + toInsert;
            if(!lineStartAt(pos-2)) {
                toInsert = '\n' + toInsert;
            }
        }
        // Check if we need to add a newline or two after
        if(!lineStartAt(pos+2)) {
            toInsert += '\n';
            if(!lineStartAt(pos+1)) {
                toInsert += '\n';
            }
        }
        textarea.val(text.substring(0, pos) + toInsert +
                text.substring(pos, text.length));
        textarea[0].selectionStart = textarea[0].selectionEnd = pos;
    }
}

function editorPreview(fieldset, textarea) {
    var preview = $('button.preview', fieldset);
    var modal = $('#editor-preview-modal');
    var modalBody = $('div.body', modal);
    preview.click(function() {
        var overlay = $('<div id="overlay">');
        $('body').append(overlay);
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
                modalBody.html(responseData['body']);
                $('figure', modalBody).each(function(i) {
                    editorPreviewImage(this, textarea, i);
                });
            }
        });
        return false;
    });
}

var imageRE = /^(#image-\d+-\w+ *)$/m;
function editorPreviewImage(figureElt, textarea, index) {
    $('button', figureElt).click(function() {
        figureElt.className = $(this).data('class');
        $('img', figureElt).attr('src', $(this).data('url'));
        // Insert tag in our textarea
        var textParts = textarea.val().split(imageRE);
        textParts[1 + index * 2] = $(this).data('tag');
        textarea.val(textParts.join(""));
    });
}

});
