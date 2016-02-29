/*
thesquirrel.org

Copyright (C) 2016 Flying Squirrel Community Space

thesquirrel.org is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

thesquirrel.org is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with thesquirrel.org.  If not, see <http://www.gnu.org/licenses/>.
*/

(function() {

   var storageKey = 'hiddenOverlayBanners';

$(document).ready(function() {
    $('.overlay-banner').each(overlayBanner);
})

function overlayBanner() {
    var banner = $(this);
    var closeButton = $('button.close', this);
    var bannerId = banner.data('id');
    var storageKey = 'hiddenOverlayBanner' + bannerId;

    if(localStorage.getItem(storageKey) !== '1') {
        banner.show();
    }
    closeButton.click(function() {
        banner.hide();
        localStorage.setItem(storageKey, '1');
    });
}


})();
