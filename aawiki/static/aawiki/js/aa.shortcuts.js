/**
 * This file is part of Active Archives.
 * Copyright 2006-2012 the Active Archives contributors (see AUTHORS)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Also add information on how to contact you by electronic and paper mail.
 */


$(function() {
    // maintain variable currentTextArea
    $("section textarea", AA.$.canvas).live("focus", function () {
        AA.currentTextArea = this;
    }).live("blur", function () {
        AA.currentTextArea = undefined;
    });

    shortcut.add("Ctrl+Shift+Down", function () {
        if (AA.currentTextArea) {
            var player = AA.utils.firstPlayer();
            if (player) {
                var ct = $.timecode_fromsecs(player.currentTime, true);
                $.insertAtCaret(currentTextArea, ct + " -->", true);
            }
            //var d = new Date();
            //var ct = [$.zeropad(d.getHours(), 2), $.zeropad(d.getMinutes(), 2), $.zeropad(d.getSeconds(), 2)].join(':');
            //$.insertAtCaret(currentTextArea, ct + " -->", true);

        }
    });

    shortcut.add("Ctrl+Shift+Left", function () {
        $(".player", AA.config.elts.canvas).each(function () {
            this.currentTime -= 5;
        });
    });

    shortcut.add("Ctrl+Shift+Right", function () {
        $(".player", AA.config.elts.canvas).each(function () {
            this.currentTime += 5;
        });
    });

    shortcut.add("Ctrl+Shift+Up", function () {
        $(".player", AA.config.elts.canvas).each(function () {
            if (this.paused) { 
                this.play(); 
            } else { 
                this.pause(); 
            }
        });
    });
});
