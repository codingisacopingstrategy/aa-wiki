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


(function( $ ){
    var methods = {
        init : function (options) { 
            console.log(options);

            var settings = $.extend( {
                target : 'body',
                end : function () {}
            }, options);

            return this.each(function () {
                $(this).buttonset().find("input").on("change", function() {
                    var classes = [],
                        mode = $(this).val();

                    $(this).parent().find('input').each(function(i, selected) {
                        classes[i] = $(selected).val();
                    });

                    classes = classes.join(' ').replace(mode, '');

                    $(settings.target).removeClass(classes).addClass(mode);


                    options.end.call(this);

                    //if (mode == "cinematic") {
                        //$("body").layout().close("west");
                    //} else {
                        //$("body").layout().open("west");
                    //}
                });
            })
        }
    };

    $.fn.classSwitcher = function( method ) {
        // Method calling logic
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || ! method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jquery.aa.classSwitcher');
        }        
    };
})( jQuery );
