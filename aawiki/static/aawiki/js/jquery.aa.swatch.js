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


(function($){
    var methods = {
        init : function (options) { 
            $("section").droppable({
                greedy: true,
                accept: ".swatch",
                hoverClass: "drophover",
                drop: function (event, ui) {
                    var $select = $(ui.helper).find('select');
                    var key = $select.attr("id");
                    var value = $select.find('option:selected').val();
                    var section = $(this).closest(".section1, .section2");
                    section.css(key, value);
                    section.trigger('geometrychange');
                }
            });

            return this.each(function (i) {
                $(this).draggable({
                    helper: function () {
                        var $this = $(this);
                        var $clone = $this.clone();
                        $clone.find('select').first().val($this.find('select').first().val());
                        return $clone.appendTo("body");
                    }
                });
            })
        },
        destroy: function () { 
            return this.each(function(){
            })
        }
    };

    $.fn.swatch = function( method ) {
        // Method calling logic
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || ! method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jquery.aa.swatch');
        }        
    };
})(jQuery);
