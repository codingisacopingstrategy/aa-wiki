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


//<menu type="toolbar">
  //<li>
    //<menu label="File">
      //<button type="button" onclick="new()">New...</button>
      //<button type="button" onclick="save()">Save...</button>
    //</menu>
  //</li>
  //<li>
    //<menu label="Edit">
      //<button type="button" onclick="cut()">Cut...</button>
      //<button type="button" onclick="copy()">Copy...</button>
      //<button type="button" onclick="paste()">Paste...</button>
    //</menu>
  //</li>
//</menu>
//<menu>
//<command type="command" label="Save" onclick="save()">Save</command>
//</menu>


(function ($) {
    $(document).ready(function() {
        var menu;

        function singleClick(event) {
            if (! menu) {
                menu = $("<ul><li><button><i class='icon-plus'></i> Create annotation</button></li></ul>").css({
                    left: event.clientX,
                    top: event.clientY,
                    position: "absolute"
                }).appendTo($("body"));
            } else {
                menu.remove()
                menu = undefined;
            };
        }

        function doubleClick(event) {
            if (! menu) {
                menu = $("<ul><li><button><i class='icon-plus'></i> Create foobar</button></li></ul>").css({
                    left: event.clientX,
                    top: event.clientY,
                    position: "absolute"
                }).appendTo($("body"));
            } else {
                menu.remove()
                menu = undefined;
            };
        }

        $("html").click(function(event) {
            var that = this;
            setTimeout(function() {
                var dblclick = parseInt($(that).data('double'), 10);
                if (dblclick > 0) {
                    $(that).data('double', dblclick-1);
                } else {
                    singleClick.call(that, event);
                }
            }, 300);
        }).dblclick(function(event) {
            $(this).data('double', 2);
            doubleClick.call(this, event);
        });

        // I really don't know why, but when we don't handle the mousedown event here 
        // double-clicking the page does select some object (the first child of body 
        // on Firefox and the nearest element on Chrome)
        $('html').bind('mousedown', function(e) {
            return false;   
        });

    });
})(jQuery);

/* vim: set foldmethod=indent: */
